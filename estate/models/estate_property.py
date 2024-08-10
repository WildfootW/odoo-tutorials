#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyleft (ɔ) 2024 wildfootw <wildfootw@wildfoo.tw>
#
# Distributed under terms of the MIT license.

from odoo import fields, models, api
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property"

    name = fields.Char(required = True)
    active = fields.Boolean()
    state = fields.Selection(
        selection = [("new", "New"), ("offer received", "Offer Received"), ("offer accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")],
        default = "new",
        copy = False,
    )
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date("Available From", copy = False, default = fields.Date.add(fields.Date.today(), months = 3))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly = True, copy = False)
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_prientation = fields.Selection(
        selection = [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )
    total_area = fields.Float(compute="_compute_total_area", store=True)

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string = "Buyer", copy = False)
    salesperson_id = fields.Many2one("res.users", string = "Salesperson", default = lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string = "Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_prientation = 'north'
        else:
            self.garden_area = 0
            self.garden_prientation = False

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold properties cannot be cancelled.")
            record.state = 'cancelled'
        return True

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cancelled properties cannot be sold.")
            record.state = 'sold'
        return True

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"

    name = fields.Char(required = True)

    from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char(required = True)

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"

    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = fields.Date.add(start_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                create_date = record.create_date.date()
                delta = record.date_deadline - create_date
                record.validity = delta.days
            else:
                record.validity = 7

    def action_accept(self):
        for record in self:
            if record.property_id.state == 'sold':
                raise UserError("You cannot accept an offer for a sold property.")
            if any(offer.status == 'accepted' for offer in record.property_id.offer_ids):
                raise UserError("Only one offer can be accepted for a property.")
            record.status = 'accepted'
            record.property_id.state = 'sold'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True
