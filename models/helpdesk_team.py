from odoo import models, fields, api

# The purpose of this inheritance is to modify the built in helpdesk ticket model.
# Helpdesk team selection field has been added to facilitate ticket creation, storing it in the desired team or channel.
# This reduces redundancy of having too many channels, having the same form fields in website view.

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    helpdesk_team_selection = fields.Selection(
        selection='_get_helpdesk_team_selection',
        string="Help Team",
        help="Used only for website submissions",
    )

    @api.model
    def _get_helpdesk_team_selection(self):
        teams = self.env['helpdesk.team'].search([])
        # Return as a list of tuples (value, label)
        return [(str(team.id), team.name) for team in teams]
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            team_selection = vals.get('helpdesk_team_selection')

            if team_selection:
                # Convert selection (string) → team_id (int)
                team = self.env['helpdesk.team'].browse(int(team_selection))

                if team.exists():
                    vals['team_id'] = team.id

                    # Optional but recommended
                    if team.company_id:
                        vals.setdefault('company_id', team.company_id.id)

                # Cleanup: avoid storing redundant data
                vals.pop('helpdesk_team_selection', None)

        return super().create(vals_list)

