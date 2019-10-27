from marshmallow import Schema, fields, pprint, post_load, pre_dump, post_dump


class LinkSchema(Schema):

  previous = fields.Str()
  current = fields.Str()
  following = fields.Str()
  
  @post_dump
  def create_links(self, data, **kwargs):

    ## Creating response envelope
    return {"links": data}
