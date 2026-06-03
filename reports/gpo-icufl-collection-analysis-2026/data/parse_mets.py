"""
This scripts goes through a copy of all the METS files from the GPO ICUFL collection and extracts some minimal metadata to help navigate the items and link the disk image files with their contexts
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import csv

# Namespaces
ns = {
    'mets': "http://www.loc.gov/METS/",
    'mods' : "http://www.loc.gov/mods/v3",
    'xlink': "http://www.w3.org/1999/xlink"
}
# Qualified attribute name:
href_attrib = f"{{{ns['xlink']}}}href"


# Open a CSV file for output:
with open('gpo-icufl-items.csv', 'w', newline='') as csv_file:
    items_writer = csv.writer(csv_file)
    items_writer.writerow(['item_id', 'title', 'date', 'publisher', 'fids', 'fnames'])

    # Loop through the METS files:
    path_list = Path('mets').glob('*.xml')
    for path in path_list:
    
        # Parse the XML:
        tree = ET.parse(path)
        root = tree.getroot()

        # Get the local item ID
        item_id = None
        for identifier in root.findall('mets:dmdSec/mets:smdWrap/mets:xmlData/mods:mods/mods:identifier', ns):
            if identifier.attrib['type'] == 'local':
                item_id = identifier.text
        # A check that something hasn't gone terribly wrong:
        if not item_id or not path.name.startswith(item_id):
            print(item_id,str(path))
            raise Exception(f"File {path} does not contain a matching mods:identifier metadata field!")
        
        # Get the (first) title and date:
        title = root.find('mets:dmdSec/mets:smdWrap/mets:xmlData/mods:mods/mods:titleInfo/mods:title',ns)
        date = root.find('mets:dmdSec/mets:smdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:dateIssued',ns)
        if date != None:
            date = date.text
        publisher = root.find('mets:dmdSec/mets:smdWrap/mets:xmlData/mods:mods/mods:originInfo/mods:publisher',ns)
        if publisher != None:
            publisher = publisher.text


        # Get file ids and names:
        fids = []
        fnames = []
        for file in root.findall('mets:fileSec/mets:fileGrp/mets:file', ns):
            fid = file.attrib['ID']
            flocat = file.find('mets:FLocat', ns)
            fname = flocat.attrib[href_attrib]
            fids.append(fid)
            fnames.append(fname)

        # Write to CSV:
        items_writer.writerow([item_id, title.text, date, publisher, "|".join(fids), "|".join(fnames)])

