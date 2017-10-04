from django import forms
from autocomplete_light import shortcuts as al
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div
from .models import ExtractCharity
from .models import budget_flow


class query_name(forms.Form):
    kind = forms.ChoiceField(widget=forms.Select,
                             choices=(('1', 'Institution'), ('2', 'Trustee'), ('3', 'Area of benefit'), ('4', 'Regno')))
    name = forms.CharField(label="Search")

    def __init__(self, *args, **kwargs):
        super(query_name, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search', css_class="search_btn"))


class search_form_pdfs(forms.Form):
    search = forms.CharField(label="Search")

    def __init__(self, *args, **kwargs):
        super(search_form_pdfs, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search', css_class="search_btn"))


class form_user_login(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(form_user_login, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Login'))


class select_inst(forms.Form):
    class Meta:
        Model = ExtractCharity

    regno = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    aob = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    include = forms.BooleanField(required=False, )
# def __init__(self, *args, **kwargs):
#	super(select_inst, self).__init__(*args, **kwargs)
#	if self.instance.pdfs == False:
#		self.fields['include'].widget.attrs['readonly']=True


class FormSet1Helper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FormSet1Helper, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.form_method = 'post'
        # self.form_action=reverse('add_text_crispy')
        self.form_tag = False

    # self.form_class = 'Formset1'
    # self.layout = Layout(
    # Fieldset(Div('formset1',css_id='Formset1')))
    # self.render_required_fields = True
    # self.add_input(Submit('submit', 'Submit'))


class form_update_pdfs(forms.Form):
    class Meta:
        Model = budget_flow

    id = forms.CharField(widget=forms.HiddenInput(), required=False)

    recip_don = forms.CharField(label="Donor/Recipient", widget=al.TextWidget('donor_recipient'))
    # recip_don = autocomplete_light.TextWidget('donor_recipient')
    kind_recip_don = forms.ChoiceField(label="Donor/Recipient kind", widget=forms.Select, choices=(
    ('Person', 'Natural Person'), ('corp', 'Corporation'), ('charity', 'Charity'), ('tt', 'Think Tank'),
    ('lawF', 'Law Firm'), ('marketF', 'Marketing Firm'), ('gov', 'Governmental Body'), ('oth', 'other')))
    # url_recip_don = forms.URLField(label='URL of the recipient/donor', required=False)
    type_of_flow = forms.ChoiceField(label="Type of flow", widget=forms.Select,
                                     choices=(('in', 'Income'), ('out', 'Expenditure')))
    amount = forms.IntegerField(label="Amount")
    currency = forms.ChoiceField(label="Currency", widget=forms.Select,
                                 choices=(('Pounds', 'Pounds'), ('Euro', 'Euro'), ('Dollar', 'Dollar')))
    nmb_of_grants = forms.IntegerField(label="Number of grants if applicable", required=False)
    notes_grants = forms.CharField(label="Notes on the grants", required=False, widget=forms.Textarea)


# notes_recip_don = forms.CharField(label="Notes on the recipient/donor", required=False,widget=forms.Textarea)


class form_update_pdfs_2(forms.Form):
    finalized = forms.BooleanField(required=False, label="Finalized")
    no_data = forms.BooleanField(required=False, label="No data")
    not_interested = forms.BooleanField(required=False, label="Charity not interesting")
    not_interested_text = forms.CharField(label="Explanation",
                                          help_text="If you checked 'Charity not interesting' please specify here why you think the charity is not of interest.",
                                          required=False, widget=forms.Textarea)
    notes_pdf = forms.CharField(label="Notes on the pdf", required=False, widget=forms.Textarea)
    cp_descr = forms.CharField(label="Definition of copied Field",
                               help_text="Please use this field to define the copied area. Use the following words: 'name' (for the name of the institution), amount (for the amount of money) and 'disc' (for a sequence on non-shitespace characters to discard). E.g.: 'name amount disc' would match a table containing the name, the money flow and a sum column we dont want to capture.",
                               required=False)
    cp_kind = forms.ChoiceField(label="Type of flows", required=False, widget=forms.Select,
                                choices=(('in', 'Income'), ('out', 'Expenditure')))
    currency = forms.ChoiceField(label="Currency", required=False, widget=forms.Select,
                                 choices=(('Pounds', 'Pounds'), ('Euro', 'Euro'), ('Dollar', 'Dollar')))
    cp_multi = forms.IntegerField(label="Multiplier", required=False,
                                  help_text="Some pdfs use multipliers in their sheets. Use this field to define it.")
    cp_delete = forms.BooleanField(label="Delete existing flows?", required=False)
    cp_field = forms.CharField(label="Drop copied part here", required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(form_update_pdfs_2, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class form_search_results(forms.Form):
    search = forms.CharField(label="Search")

    def __init__(self, *args, **kwargs):
        super(form_search_results, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Search', css_class="search_btn"))
