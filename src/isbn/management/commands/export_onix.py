# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.utils import timezone

from isbn.models import ONIXRecord

HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<ONIXMessage release="3.0"
    xmlns="http://ns.editeur.org/onix/3.0/reference"
    xmlns:schemaLocation="https://e-isbn.pl/IsbnWeb/schemas/ONIX_BookProduct_3.0_reference.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <Header>
        <Sender>
            <SenderName>Fundacja NOWOCZESNA POLSKA</SenderName>
            <ContactName>Paulina Choromańska</ContactName>
            <EmailAddress>paulinachoromanska@nowoczesnapolska.org.pl</EmailAddress>
        </Sender>
        <SentDateTime>%s</SentDateTime>
        <MessageNote>Opis wygenerowany przez wydawcę</MessageNote>
        <DefaultLanguageOfText>pol</DefaultLanguageOfText>
    </Header>"""

PRODUCT = """
    <Product datestamp="%(datestamp)s">
        <RecordReference>%(record_reference)s</RecordReference>
        <NotificationType>03</NotificationType>
        <RecordSourceType>01</RecordSourceType>
        <RecordSourceName>Fundacja NOWOCZESNA POLSKA</RecordSourceName>
        <ProductIdentifier>
            <ProductIDType>15</ProductIDType>
            <IDValue>%(isbn)s</IDValue>
        </ProductIdentifier>
        <DescriptiveDetail>
            <ProductComposition>00</ProductComposition>
            <ProductForm>%(product_form)s</ProductForm>%(product_form_detail)s
            <TitleDetail>
                <TitleType>01</TitleType>
                <TitleElement>
                    <TitleElementLevel>01</TitleElementLevel>%(part_number)s
                    <TitleText>%(title)s</TitleText>
                </TitleElement>
            </TitleDetail>%(contributors)s
            <EditionType>%(edition_type)s</EditionType>
            <EditionNumber>%(edition_number)s</EditionNumber>
            <Language>
                <LanguageRole>01</LanguageRole>
                <LanguageCode>%(language)s</LanguageCode>
            </Language>
        </DescriptiveDetail>
        <PublishingDetail>
            <Imprint>
                <ImprintName>%(imprint)s</ImprintName>
            </Imprint>
            <Publisher>
                <PublishingRole>01</PublishingRole>
                <PublisherName>Fundacja NOWOCZESNA POLSKA</PublisherName>
            </Publisher>
            <CityOfPublication>Warszawa</CityOfPublication>
            <CountryOfPublication>PL</CountryOfPublication>
            <PublishingDate>
                <PublishingDateRole>01</PublishingDateRole>
                <Date>%(publishing_date)s</Date>
            </PublishingDate>
            <PublishingDate>
                <PublishingDateRole>09</PublishingDateRole>
                <Date>%(publishing_date)s</Date>
            </PublishingDate>
        </PublishingDetail>
    </Product>"""

PRODUCT_FORM_DETAIL = """
            <ProductFormDetail>%s</ProductFormDetail>"""

PART_NUMBER = """
                    <PartNumber>%s</PartNumber>"""

CONTRIBUTOR = """
            <Contributor>
                <SequenceNumber>%(no)s</SequenceNumber>
                <ContributorRole>%(role)s</ContributorRole>%(identifier)s%(name)s%(corporate_name)s%(unnamed)s%(birth_date)s%(death_date)s
            </Contributor>"""

NAME_IDENTFIER = """
                <NameIdentifier>
                    <NameIDType>16</NameIDType>
                    <IDValue>%(isni)s</IDValue>
                </NameIdentifier>"""

NAME = """
                <PersonNameInverted>%s</PersonNameInverted>"""

CORPORATE_NAME = """
                <CorporateName>%s</CorporateName>"""

UNNAMED = """
                <UnnamedPersons>%s</UnnamedPersons>"""

CONTRIBUTOR_DATE = """
                <ContributorDate>
                    <ContributorDateRole>%(role)s</ContributorDateRole>
                    <Date>%(date)s</Date>
                </ContributorDate>"""

FOOTER = """
</ONIXMessage>"""


class Command(BaseCommand):
    help = "Export ONIX."

    def handle(self, *args, **options):
        xml = HEADER % timezone.now().strftime('%Y%m%dT%H%M%z')
        for record in ONIXRecord.objects.all():
            xml += self.render_product(record)
        xml += FOOTER
        print xml.encode('utf-8')

    def render_product(self, record):
        if record.product_form_detail:
            product_form_detail = PRODUCT_FORM_DETAIL % record.product_form_detail
        else:
            product_form_detail = ''
        if record.part_number:
            part_number = PART_NUMBER % record.part_number
        else:
            part_number = ''
        contributors = ''
        for no, contributor in enumerate(record.contributors, start=1):
            contributors += self.render_contributor(no, contributor)
        return PRODUCT % {
            'datestamp': record.datestamp.strftime('%Y%m%d'),
            'record_reference': record.reference(),
            'isbn': record.isbn(),
            'product_form': record.product_form,
            'product_form_detail': product_form_detail,
            'part_number': part_number,
            'title': record.title,
            'contributors': contributors,
            'edition_type': record.edition_type,
            'edition_number': record.edition_number,
            'language': record.language,
            'imprint': record.imprint,
            'publishing_date': record.publishing_date.strftime('%Y%m%d'),
        }

    @staticmethod
    def render_contributor(no, contributor):
        if 'isni' in contributor:
            identifier = NAME_IDENTFIER % contributor
        else:
            identifier = ''
        if 'name' in contributor:
            name = NAME % contributor['name']
        else:
            name = ''
        if 'corporate_name' in contributor:
            corporate_name = CORPORATE_NAME % contributor['corporate_name']
        else:
            corporate_name = ''
        if 'unnamed' in contributor:
            unnamed = UNNAMED % contributor['unnamed']
        else:
            unnamed = ''
        if 'birth_date' in contributor:
            birth_date = CONTRIBUTOR_DATE % {'role': '50', 'date': contributor['birth_date']}
        else:
            birth_date = ''
        if 'death_date' in contributor:
            death_date = CONTRIBUTOR_DATE % {'role': '51', 'date': contributor['death_date']}
        else:
            death_date = ''
        return CONTRIBUTOR % {
            'no': no,
            'role': contributor['role'],
            'identifier': identifier,
            'name': name,
            'corporate_name': corporate_name,
            'unnamed': unnamed,
            'birth_date': birth_date,
            'death_date': death_date,
        }
