from property.models import PropertyForms


def update_property_forms(property_management, payload):
    existing_forms = set(
        PropertyForms.objects.filter(property=property_management)
        .values_list("form_id", flat=True)
    )

    new_forms = set(payload.forms)

    # forms to add
    forms_to_add = new_forms - existing_forms

    # forms to delete
    forms_to_delete = existing_forms - new_forms

    # add new forms
    PropertyForms.objects.bulk_create(
        [
            PropertyForms(property=property_management, form_id=form_id)
            for form_id in forms_to_add
        ]
    )

    # delete removed forms
    PropertyForms.objects.filter(
        property=property_management,
        form_id__in=forms_to_delete
    ).delete()