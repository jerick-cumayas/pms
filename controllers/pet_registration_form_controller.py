from odoo import http
from odoo.http import request

from .routes import FORM_PET_REGISTRATION_PATH, FORM_THANK_YOU_PATH


class PetRegistrationFormController(http.Controller):
    @http.route(
        f"{FORM_PET_REGISTRATION_PATH}",
        auth="public",
        website=True,
        name="pet_registration_form",
    )
    def pet_registration_form(self, **kwargs):
        # Logged user
        logged_user = request.env.user.partner_id
        return request.render(
            "pms.website_pet_registration_form",
            {
                "user": logged_user,
            },
        )

    @http.route(
        f"{FORM_PET_REGISTRATION_PATH}/submit",
        type="http",
        auth="public",
        website=True,
        csrf=True,
        name="amenities_form_submit",
    )
    def pet_registration_form_submit(self, **post):
        requestor_id = post.get("requestor_id")
        if not requestor_id:
            return request.render(
                "website_pet_registration_form", {"error": "Owner not found."}
            )

        registration = (
            request.env["form.pet_registration"]
            .sudo()
            .create({"requestor_id": int(requestor_id), "state": "submitted"})
        )

        pet_names = request.httprequest.form.getlist("pet_name[]")
        pet_species = request.httprequest.form.getlist("pet_species[]")
        pet_breeds = request.httprequest.form.getlist("pet_breed[]")
        pet_ages = request.httprequest.form.getlist("pet_age[]")
        pet_genders = request.httprequest.form.getlist("pet_gender[]")
        pet_details = request.httprequest.form.getlist("pet_details[]")
        pet_is_vaccinated = request.httprequest.form.getlist("pet_is_vaccinated[]")

        pet_list_for_ticket = []
        pet_model = request.env["pet.details"].sudo()
        for i in range(len(pet_names)):
            pet = pet_model.create(
                {
                    "registration_id": registration.id,
                    "name": pet_names[i],
                    "species": pet_species[i],
                    "breed": pet_breeds[i],
                    "age": int(pet_ages[i]) if pet_ages[i] else 0,
                    "gender": pet_genders[i],
                    "details": pet_details[i],
                    "is_vaccinated": bool(pet_is_vaccinated[i])
                    if i < len(pet_is_vaccinated)
                    else False,
                }
            )
            pet_list_for_ticket.append(
                f"Name: {pet.name}, Species: {pet.species}, Breed: {pet.breed}, "
                f"Age: {pet.age}, Gender: {pet.gender}, "
                f"Vaccinated: {'Yes' if pet.is_vaccinated else 'No'}, "
                f"Details: {pet.details}"
            )

        team = (
            request.env["helpdesk.team"]
            .sudo()
            .search([("name", "ilike", "Pet Registrations")], limit=1)
        )

        # Create helpdesk ticket (STORE the record!)
        ticket = (
            request.env["helpdesk.ticket"]
            .sudo()
            .create(
                {
                    "name": f"New Pet Registration for Owner {requestor_id}",
                    "description": "\n".join(pet_list_for_ticket),
                    "partner_id": int(requestor_id),
                    "team_id": team.id if team else False,
                    "form_id": registration.id,
                    "form_model": registration._name,
                }
            )
        )

        # Link ticket back to the form
        registration.write(
            {
                "helpdesk_ticket_id": ticket.id,
            }
        )

        return request.redirect(f"{FORM_THANK_YOU_PATH}")

    # def pet_registration_form_submit(self, **post):
    #     """
    #     Handles the website pet registration form submission.
    #     """

    #     # Get the owner
    #     owner_id = post.get('owner_id')
    #     if not owner_id:
    #         return request.render('website_pet_registration_form', {
    #             'error': 'Owner not found.'
    #         })

    #     # Create the main registration record
    #     registration = request.env['form.pet_registration'].sudo().create({
    #         'owner_id': int(owner_id),
    #     })

    #     # Arrays from form submission
    #     pet_names = post.getlist('pet_name[]')
    #     pet_species = post.getlist('pet_species[]')
    #     pet_breeds = post.getlist('pet_breed[]')
    #     pet_ages = post.getlist('pet_age[]')
    #     pet_genders = post.getlist('pet_gender[]')
    #     pet_details = post.getlist('pet_details[]')
    #     pet_is_vaccinated = post.getlist('pet_is_vaccinated[]')  # note: checkboxes send 'on' if checked

    #     # Loop through each pet and create pet.details records
    #     for i in range(len(pet_names)):
    #         request.env['pet.details'].sudo().create({
    #             'registration_id': registration.id,
    #             'name': pet_names[i],
    #             'species': pet_species[i],
    #             'breed': pet_breeds[i],
    #             'age': int(pet_ages[i]) if pet_ages[i] else 0,
    #             'gender': pet_genders[i],
    #             'details': pet_details[i],
    #             'is_vaccinated': bool(pet_is_vaccinated[i]) if i < len(pet_is_vaccinated) else False,
    #         })

    #     # Redirect or render a thank-you page
    #     return request.redirect(f'{FORM_THANK_YOU_PATH}')
