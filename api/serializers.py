from rest_framework import serializers
from tables.models import TableBluePrint, TableFieldBluePrint, TableInstance, TableInstanceField, Database
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response


class TableFieldBluePrintSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableFieldBluePrint
        exclude = ('table_blue_print', 'id',)

class GetTableBluePrintSerializer(serializers.ModelSerializer):
    fields = TableFieldBluePrintSerializer(many=True)

    class Meta:
        model = TableBluePrint
        fields = ['name', 'fields', 'user']
    
class GetDatabaseSerializer(serializers.ModelSerializer):
    tables = GetTableBluePrintSerializer(many=True)

    class Meta:
        model = Database
        fields = ['id', 'name', 'allowed_origins', 'tables']

class PostDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = ['name', 'allowed_origins', 'user']

class CreateTableBluePrintSerializer(serializers.ModelSerializer):
    fields = TableFieldBluePrintSerializer(many=True)

    class Meta:
        model = TableBluePrint
        fields = ['name', 'fields', 'user', 'database']


    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        table_blue_print = TableBluePrint.objects.create(**validated_data)

        TableFieldBluePrint.objects.bulk_create([TableFieldBluePrint(table_blue_print=table_blue_print,**field_data) for field_data in   fields_data])

        return table_blue_print

def CreateTableInstanceSerializer(JSON_data, blue_print, table_instance, headers):
    if not isinstance(JSON_data, dict):
        return Response({"detail": f"invalid data for {blue_print.name}"}, status=400, headers=headers)


    table_fields = blue_print.fields.values_list('name', 'type')

    field_types ={
        'char': ('character_field', str),
        'bool': ('boolean_field', bool),
        'int': ('integer_field', int),
        'json': ('JSON_field', dict),
        'text': ('text_field', str),
    }

    table_field_names = [field[0] for field in table_fields]
    table_field_types = {field[0]: field_types[field[1]][0] for field in table_fields}
    table_field_blue_prints = {field.name: field for field in blue_print.fields.all()}

    # check for undefined field names
    for field_name in JSON_data.keys():
        if field_name not in table_field_names:
            return Response({"detail": f"{field_name} is not a valid field name"}, status=400, headers=headers)

    # validate fields data type
    for field_name, field_blue_print in table_field_blue_prints.items():
        if field_name not in JSON_data.keys(): continue
        if not isinstance(JSON_data[field_name], field_types[field_blue_print.type][1]):
            return Response({"detail": f"invalid data type for {field_name}"}, status=400, headers=headers)

    JSON_data_fields = tuple(JSON_data.keys())
    table_instance_fields = TableInstanceField.objects.filter(table_instance__table_blue_print=blue_print.id)

    existing_values = {name: [] for name in table_field_names}
    unique_validation_exclude = {}
    if table_instance != None:
        unique_validation_exclude['table_instance'] = table_instance.id

    for name in table_field_names:
        existing_fields = table_instance_fields.filter(table_field_blue_print__name=name).exclude(**unique_validation_exclude)
        existing_fields_values = existing_fields.values_list(table_field_types[name], flat=True)
        existing_values[name] = list(existing_fields_values)

    empty_field = {
        'char': {"default": 'default_character_field', "empty": ""},
        'bool': {"default": 'default_boolean_field', "empty": None},
        'int': {"default": 'default_integer_field', "empty": None},
        'json': {"default": 'default_JSON_field', "empty": None},
        'text': {"default": 'default_text_field', "empty": ""},
    }
    
    for field_name in table_field_names:
        field_blue_print = blue_print.fields.get(name__iexact=field_name)

        # check for missing fields
        if field_name not in JSON_data_fields and table_instance == None:
            if field_blue_print.has_default:
               JSON_data[field_name] = getattr(field_blue_print, empty_field[field_blue_print.type]['default'])
            elif field_blue_print.blank:
               JSON_data[field_name] = empty_field[field_blue_print.type]['empty']
            else:
               return Response({"detail": f"{field_name} field must be included"}, status=400, headers=headers)
            
        # validate unique fields
        if field_name not in JSON_data.keys(): continue
        if existing_values[field_name].count(JSON_data[field_name]) == 0: continue
        if field_blue_print.unique:
            return Response({"detail": f"{field_name} field must be unique"}, status=400, headers=headers)
    
    if table_instance == None:
        table_instance = TableInstance.objects.create(table_blue_print=blue_print)

        def instance_fields_data(name):
            data = {
                'table_instance': table_instance,
                'table_field_blue_print' : table_field_blue_prints[name],
                table_field_types[name]: JSON_data[name]
            }
            return data
            
        instance_fields = [TableInstanceField(**instance_fields_data(name)) for name in JSON_data.keys()]

        TableInstanceField.objects.bulk_create(instance_fields)
    else:
        fields = table_instance.fields.filter(table_field_blue_print__name__in=JSON_data.keys())
        field_names = {field_types[field.table_field_blue_print.type][0] for field in fields}
        print(field_names)

        for field in fields:
            setattr(field, field_types[field.table_field_blue_print.type][0], JSON_data[field.table_field_blue_print.name])

        TableInstanceField.objects.bulk_update(fields, field_names)

    return Response(JSON_data, headers=headers)
      


def GetTableInstanceSerializer(blue_print, table_instances):
    table_fields = blue_print.fields.values_list('name', 'type')
    field_types ={
        'char': 'character_field',
        'bool': 'boolean_field',
        'int': 'integer_field',
        'json': 'JSON_field',
        'text': 'text_field',
    }

    def instanceSerializer(instance):
        instance_fields = {field.table_field_blue_print.name: field for field in instance.fields.all()}
        return {field[0]: getattr(instance_fields[field[0]], field_types[field[1]]) for field in table_fields}
   
    JSON_data = [instanceSerializer(instance) for instance in table_instances]
    return JSON_data
    


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token