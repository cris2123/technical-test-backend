from marshmallow import Schema, fields, pprint, post_load, pre_dump, post_dump
class ErrorSchema(Schema):

  status = fields.Str()
  title = fields.Str()
  source = fields.Str()
  detail = fields.Str()

  @post_dump()
  def create_error(self, data, **kwargs):
    """ Function to wrap my error objects """
    return({'error': data})
