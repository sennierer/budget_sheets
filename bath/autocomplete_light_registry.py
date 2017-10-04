import autocomplete_light
from models import ExtractCharity

class donor_recipient(autocomplete_light.AutocompleteModelBase):
	search_fields = ['name']

autocomplete_light.register(ExtractCharity,donor_recipient,autocomplete_js_attributes={
	'minimum_characters':3})