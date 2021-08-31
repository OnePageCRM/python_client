===============================
OnePageCRM Python Client
===============================

Connect and interface with the OnePageCRM REST API

Installation
============

::

    pip install onepagecrm

Usage
=====

The first thing to do is to set up your client

.. code-block:: python

    from onepagecrm import OnePageCRMAPI, RequestError, UnknownError
    # Replace the user_id and api_key with your values
    client = OnePageCRMAPI(user_id, api_key)

Once you have your client set up you can start making requests.

Getting data:

.. code-block:: python

    contacts = client.get('contacts')['contacts']

    # Limit returned data
    email_addresses = []
    for contact in client.get('contacts', fields='emails', sparse=True)['contacts']:
        emails = contact['contact'].get('emails')
        if emails:
            email_addresses.extend([e.get('value') for e in emails])

    # Filter data
    contacts = client.get('contacts', if_modified_since='2014-07-10')

    # Paginate
    contacts = client.get('contacts', page=2, per_page=25)

    # Sorting and Ordering
    contacts = client.get('contacts', sort_by='modified_at', order='asc')


Create new resources:

.. code-block:: python

    contact = client.post('contacts', {'first_name': 'Michael',
                                       'last_name': 'Fitzgerald',
                                       'company_name': 'OnePageCRM'})['contact']
    contact_id = contact['id']

    text = 'Had a meeting today in cafe 47 with Michael to discuss new features'
    note = client.post('notes', {'text': text,
                                 'contact_id': contact_id,
                                 'date': '2014-07-10'})['note']
    note_id = note['id']
    # Partial create to autofill missing fields
    deal = client.post('deals', {'name': 'Lunch costs',
                                 'amount': 12.50,
                                 'status': 'won',
                                 'contact_id': contact_id},
                                partial=True)['deal']
    deal_id = deal['id']


Update existing resources:

.. code-block:: python

    contact['background'] = 'CEO of OnePage'
    contact = client.put('contacts', contact_id, contact)['contact']

    # To do a partial update
    update = {'background': 'CEO of OnePageCRM'}
    contact = client.patch('contacts', contact_id, update)['contact']

    # To attach a note to a deal
    client.patch('notes', note_id, {'linked_deal_id': deal_id'})

Delete resources you no longer need:

.. code-block:: python

    client.delete('deals', deal_id)
    client.delete('contacts', contact_id)
    # To undo the deletion of a contact
    client.delete('contacts', contact_id, undo=True)


