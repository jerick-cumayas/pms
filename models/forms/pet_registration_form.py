from odoo import models, fields, api


class PetRegistrationForm(models.Model):
    _name = "form.pet_registration"
    _description = "Pet Registration Form"

    owner_id = fields.Many2one("res.partner", string="Owner's name", required=True)
    pet_ids = fields.One2many(
        "pet.details",  # related model
        "registration_id",  # field in pet.details linking back
        string="Pet Details",
    )


class PetDetails(models.Model):
    _name = "pet.details"
    _description = "Pet Details"

    # Link to registration form
    registration_id = fields.Many2one(
        "form.pet_registration", string="Pet Registration", ondelete="cascade"
    )

    # Pet Information
    name = fields.Char(string="Pet Name", required=True)
    species = fields.Selection(
        [("dog", "Dog"), ("cat", "Cat"), ("bird", "Bird"), ("other", "Other")],
        string="Species",
        required=True,
    )
    breed = fields.Char(string="Breed")
    age = fields.Integer(string="Age (years)")
    gender = fields.Selection([("male", "Male"), ("female", "Female")], string="Gender")
    details = fields.Text(string="Other details")
    is_vaccinated = fields.Boolean(string="Is Vaccinated?")
