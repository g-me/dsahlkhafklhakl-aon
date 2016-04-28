from django.template.defaultfilters import register

__author__ = 'mehari'


# ------------------------------------------------------------------
# Custom Filters
# ------------------------------------------------------------------
@register.filter(name='display_status')
def get_status_val(value):
    if value == 100:
        return  "OPEN"
    elif value == 101:
        return "COMPLETED"
    elif value == 102:
        return "CLOSED"
    else:
        return "Error"

@register.filter(name='get_user_name')
def get_user_name(value):
    return value.rsplit('/')[-1]


@register.filter(name='user_rating')
def get_user_rating(ratings, user):
    return ratings.get(rated_user=user)