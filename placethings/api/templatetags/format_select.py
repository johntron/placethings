from django import template

register = template.Library()

@register.simple_tag
def output_format_select():
	return '''
Output: 
<select name="format" class="format_select">
	<option value="txt">Plaintext</option>
	<option value="json">JSON</option>
	<option value="xml">XML</option>
</select>
'''