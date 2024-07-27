#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyleft (ɔ) 2024 wildfootw <wildfootw@wildfoo.tw>
#
# Distributed under terms of the MIT license.

from odoo import fields, models

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(required = True)
    active = fields.Boolean()
    state = fields.Selection(
        selection = [("New", "New"), ("Offer Received", "Offer Received"), ("Offer Accepted", "Offer Accepted"), ("Sold", "Sold"), ("Canceled", "Canceled")],
        default = "New",
        copy = False,
    )
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date("Available From", copy = False, default = fields.Date.add(fields.Date.today(), months = 3))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly = True, copy = False)
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_prientation = fields.Selection(
        selection = [("North", "North"), ("South", "South"), ("East", "East"), ("West", "West")]
    )
