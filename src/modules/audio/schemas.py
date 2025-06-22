from marshmallow import schema, fields

class AudioSchema(Schema):
    type = fields.Str(required=True)
    data = fields.Raw(required=True)
    timestamp = fields.DateTime(dump_only=True)