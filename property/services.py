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


def get_building_details(building):
    return {
            "id": building.id,
            "name": building.name,
            "address_line_1": building.address_line_1,
            "address_line_2": building.address_line_2,
            "city": building.city,
            "zipcode": building.zipcode,
            "property_management_company": building.property_management_company,
            "state_registration": building.state_registration,
            "state": {
                "id": building.state.id,
                "name": building.state.name
            },
            # "forms": forms
        }