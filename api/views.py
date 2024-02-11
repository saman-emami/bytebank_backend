from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tables.models import TableBluePrint, TableFieldBluePrint, TableInstance, Database
from .serializers import GetTableBluePrintSerializer, CreateTableBluePrintSerializer, \
    CreateTableInstanceSerializer, GetTableInstanceSerializer, GetDatabaseSerializer, \
    PostDatabaseSerializer
from rest_framework.response import Response

@api_view(['GET'])
def usernames(request, username):
    is_username_taken = User.objects.filter(username=username).exists()
    response = {'usernameExists' : is_username_taken}
    return Response(response)

@api_view(['POST'])
def register(request):
    if User.objects.filter(username=request.data.get('username')).exists():
        return Response({'detail' : 'user already exists'}, status=400)

    user = User.objects.create_user(username=request.data.get('username'), password=request.data.get('password'))
    refresh = RefreshToken.for_user(user)
    refresh['username'] = str(user.username)

    login = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    return Response(login)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def databases(request):
    if request.method == 'POST':
        request.data['user'] = request.user.id

        serializer = PostDatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    
@api_view(['GET'])
def database_names(request, name):
    is_database_name_taken = Database.objects.filter(name=name).exists()
    response = {'databaseNameExists' : is_database_name_taken}
    return Response(response)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def table_blue_prints(request):
    if request.method == 'GET':
        return get_table_blue_prints(request)
    
    return create_table_blue_print(request)

def get_table_blue_prints(request):
    databases = request.user.databases.prefetch_related('tables', 'tables__fields', 'tables__table_instances').all()
    serializer = GetDatabaseSerializer(databases, many=True)
    
    for database in serializer.data:
        for table_blue_print in database['tables']:
            blue_print = TableBluePrint.objects.get(database__name=database['name'], name=table_blue_print['name'])
            table_instances = blue_print.table_instances.all()
            table_instances_data = GetTableInstanceSerializer(blue_print, table_instances)
            table_blue_print['table_instances'] = table_instances_data

    return Response(serializer.data)

def create_table_blue_print(request):
    print(request.data)
    existing_table_blue_prints_names = TableBluePrint.objects.filter(database__name=request.data['database']).values_list('name', flat=True)
    if request.data['name'] in existing_table_blue_prints_names:
        return Response({'detail': 'table already exists'}, status=400)

    field_blue_print_names = [field['name'] for field in request.data['fields']]
    for name in field_blue_print_names:
        if field_blue_print_names.count(name) > 1:
            return Response({'detail': 'field names must be unique'}, status=400)
       
    request.data['user'] = request.user.id
    serializer = CreateTableBluePrintSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

    return get_table_blue_prints(request)



@api_view(['GET', 'DELETE'])
def table_blue_print(request, name):
    table = None
    try:
        table = TableBluePrint.objects.prefetch_related('fields').get(name__iexact=name)
    except:
        return Response({'detail': 'table does not exist'}, status=404)

    if request.method == 'GET':
        serializer = GetTableBluePrintSerializer(table)
        return Response(serializer.data)
    if request.method == 'DELETE':
        table.delete()
        return Response({'detail': f"{name} table has been successfully deleted"})

def configure_cors_header(request, database):
    allowed_origins = database.allowed_origins
    if len(allowed_origins) == 0:
        return {'Access-Control-Allow-Origin':'*'}
    
    if request.META.get("HTTP_ORIGIN") in allowed_origins :
        return {'Access-Control-Allow-Origin': request.META.get("HTTP_ORIGIN")}
    
    return {'Access-Control-Allow-Origin': 'https://bytebank.vercel.app/'}

@api_view(['GET', 'POST'])
def table_instances(request, blueprint_name, database_name):
    database = Database.objects.filter(name=database_name).first()

    if database == None:
        return Response({'detail':f'no database with the name {database_name} exists'}, status=404, headers={'Access-Control-Allow-Origin': '*'})
    
    blue_print = database.tables.prefetch_related('fields').filter(name__iexact=blueprint_name).first()

    headers = configure_cors_header(request, database)

    if blue_print == None:
        return Response({'detail':f'{database_name} has no table named {blueprint_name}'}, status=404, headers=headers)

    if request.method == 'POST':
        return CreateTableInstanceSerializer(request.data, blue_print, None, headers)
    if request.method == 'GET':
        table_instances = TableInstance.objects.prefetch_related('fields').filter(table_blue_print__name__iexact=blueprint_name)
        serializer = GetTableInstanceSerializer(blue_print, table_instances)
        return Response(serializer, headers=headers)



@api_view(['GET', 'PUT', 'DELETE'])
def table_instance(request, blueprint_name, database_name, filters):
    database = Database.objects.filter(name=database_name).first()
    
    if database == None:
        return Response({'detail':f'no database with the name {database_name} exists'}, status=404, headers={'Access-Control-Allow-Origin': '*'})
    
    blue_print = database.tables.prefetch_related('fields').filter(name__iexact=blueprint_name).first()
    
    headers = configure_cors_header(request, database)

    if blue_print == None:
        return Response({'detail':f'{database_name} has no table named {blueprint_name}'}, status=404, headers=headers)

    fields = blue_print.fields.values_list('name', 'type') 

    field_types = {
        'char': 'character_field',
        'bool': 'boolean_field',
        'int': 'integer_field',
        'json': 'JSON_field',
        'text': 'text_field',
    }
    
    field_name_to_type = {name: field_types[type] for (name, type) in fields}

    field_lookups = filters.split('&')
    field_name_lookups = {}

    for (index, field_lookup) in enumerate(field_lookups):
        field_lookups[index] = field_lookup.split('=')
        field_lookups[index][0] = field_lookups[index][0].split('--')
        if len(field_lookups[index][0]) > 2:
            return Response({'detail': f"'{'--'.join(field_lookups[index][0])}' is an invalid field lookup"}, status=400, headers=headers)
        try:
            if field_name_to_type[field_lookups[index][0][0]] == 'boolean_field':
                if field_lookups[index][1].lower() == 'true':
                    field_lookups[index][1] = True
                elif field_lookups[index][1].lower() == 'false':
                    field_lookups[index][1] = False
            elif field_name_to_type[field_lookups[index][0][0]] == 'integer_field':
                field_lookups[index][1] = int(field_lookups[index][1]) 
        except:
            return Response({'detail': "invalid field lookup"}, status=400, headers=headers)

        field_name_lookups['fields__table_field_blue_print__name'] = field_lookups[index][0][0]
        if len(field_lookups[index][0]) == 2:
            field_lookups[index][0] = f"fields__{field_name_to_type[field_lookups[index][0][0]]}__{field_lookups[index][0][1]}"
        else:
            field_lookups[index][0] = f"fields__{field_name_to_type[field_lookups[index][0][0]]}"

    field_lookups = { name:value for [name, value] in field_lookups}

    filters = {
        'table_blue_print__name__iexact': blueprint_name,
        **field_lookups,
        **field_name_lookups,
    }
    
    table_instances = None
    try:
        table_instances = TableInstance.objects.prefetch_related('fields').filter(**filters)
    except:
        return Response({'detail': "invalid field lookup"}, status=400, headers=headers)

    if table_instances.count() == 0:
        return Response({'detail': f"{blueprint_name} matching query does not exist"}, status=404, headers=headers)
    
    if request.method == 'GET':
        serializer = GetTableInstanceSerializer(blue_print, table_instances)
        if len(serializer) == 1: 
            serializer = serializer[0]
        return Response(serializer, headers=headers)
    
    if request.method == 'DELETE':
        if table_instances.count() > 1: 
            return Response({'detail': f"you can only delete instances one at a time"}, status=400, headers=headers)
        table_instances.first().delete()
        return Response({'detail': f"{blueprint_name} instance has been successfully deleted"}, status=200, headers=headers)
    
    if request.method == 'PUT':
        if table_instances.count() > 1: 
            return Response({'detail': f"you can only update instances one at a time"}, status=400, headers=headers)

        table_instance = table_instances.first()
        return CreateTableInstanceSerializer(request.data, blue_print, table_instance, headers)

    
    return Response({})
   
