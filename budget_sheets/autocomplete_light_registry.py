from autocomplete_light import shortcuts as al
from .models import ExtractCharity
from .models import budget_flow


# class donor_recipient(autocomplete_light.AutocompleteModelBase):
#	search_fields = ['name']
#	model = ExtractCharity

# autocomplete_light.register(ExtractCharity,search_fields = ('name',),autocomplete_js_attributes={'minimum_characters':3,'placeholder':'type to get suggestions'})

class donor_recipient(al.AutocompleteListBase):
    def choices_for_request(self):
        choices = []
        q = self.request.GET.get('q', '')
        # q = 'policy'
        results = ExtractCharity.objects.only('name').filter(name__contains=q.upper()).distinct()
        results2 = budget_flow.objects.only('recip_don').filter(recip_don__icontains=q)
        for x in results:
            if x.name.upper() not in choices:
                choices.append(x.name)
        for z in results2:
            if z.recip_don.upper() not in choices and z.recip_don not in choices:
                choices.append(z.recip_don)
        return choices


al.register(donor_recipient, autocomplete_js_attributes={'minimum_characters': 3,
                                                                         'placeholder': 'type to get suggestions'},
                            widget_js_attributes={'max_values': 6})
# autocomplete_light.register(donor_recipient,attrs={'data-autcomplete-minimum-characters':3,'placeholder':'type to get suggestions'},widget_attrs = {'data-widget-maximum-values':6})


# ,widget_js_attributes = {'max_values': 6}
