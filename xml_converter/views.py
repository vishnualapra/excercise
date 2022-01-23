import os
from xml.etree import ElementTree

from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


def generate_response_format(data):
    """
    This function will generate the json format from the xml root
    tag based on certain conditions
    """

    response = {}

    # checking the element have inner elements
    if len(data) > 0:

        # looping over inner element
        for tag in data:

            # getting clones of  element tag from same parent
            clones = data.findall(tag.tag)

            # if multiple tag with same name present we create  with "es" at the end
            if len(clones) > 1:
                key = str(tag.tag) + "es"
            else:
                key = str(tag.tag)

            # checking tag is not attached to response and have inner items
            if key not in response and len(tag) > 0:
                response[key] = []
                # looping over same tags from a parent and generate response format using Recursion
                for item in clones:
                    response[key].append(
                        {item.tag:
                            [{item_key: item_value} for item_key, item_value in generate_response_format(item).items()]
                         }
                    )

            # if the key is not present in the response, adding the key to response with tag text as value
            elif key not in response:
                response[key] = tag.text if tag.text else ""

    # if no inner item in root, generating the response object with empty value or tag text  given
    else:
        response[data.tag] = data.text if data.text else ""
    return response


def upload_page(request):
    if request.method == 'POST':

        # getting file from user
        xml_file = request.FILES.get('file', None)

        # checking the given file is xml or not(same validation done in frontend side as well)
        if xml_file.name.lower().endswith('.xml'):

            # storing file
            fs = FileSystemStorage()
            filename = fs.save(xml_file.name, xml_file)

            # parsing the file
            tree = ElementTree.parse(filename)

            # getting root object from tree
            root = tree.getroot()

            # deleting the generated xml file
            os.remove(filename)

            # calling generate_response_format function to get the json
            data = generate_response_format(root)

            return JsonResponse(data)
    return render(request, "upload_page.html")
