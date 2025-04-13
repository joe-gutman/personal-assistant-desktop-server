from marshmallow import Schema, fields

class ChatSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    message = fields.Str(required=True)
    response = fields.Str()
    created_at = fields.DateTime(dump_only=True)