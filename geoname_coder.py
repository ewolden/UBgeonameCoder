#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geocoder
import sys, getopt
import logging

logger = logging.getLogger(__name__)
logging.disable(logging.ERROR)

COLUMNSEPERATOR = ';'

def write_to_file(output_file, geolocation, outputFormat='full'):
    if outputFormat == 'full':
        output_file.write(
            geolocation['geonamesId'] + COLUMNSEPERATOR +
            geolocation['LatLong'] + COLUMNSEPERATOR +
            geolocation['Latitiude'] + COLUMNSEPERATOR +
            geolocation['Longitude'] + COLUMNSEPERATOR +
            geolocation['Land'] + COLUMNSEPERATOR +
            geolocation['Sted'] + '\n'
            )
    elif outputFormat == 'min':
        output_file.write(
            geolocation['geonamesId'] + COLUMNSEPERATOR +
            geolocation['LatLong'] + '\n'
        )
    else:
        print('Ukjent outputformat, avslutter')
        sys.exit(2)

def write_header_to_file(output_file, outputFormat='full'):
    if outputFormat == 'full':
        output_file.write(
            'geonamesId' + COLUMNSEPERATOR +
            'LatLong' + COLUMNSEPERATOR +
            'Latitiude' + COLUMNSEPERATOR +
            'Longitude' + COLUMNSEPERATOR +
            'Land' + COLUMNSEPERATOR +
            'Sted' + '\n'
            )
    elif outputFormat == 'min':
        output_file.write(
            'geonamesId' + COLUMNSEPERATOR +
            'LatLong' + '\n'
            )
    else:
        print('Ukjent outputformat, avslutter')
        sys.exit(2)

def print_usage():
    print('\nBruk: geoname_coder.py -u <user> -i <inputfil> -o <outputfil> -f <outputformat>')
    print('-u --user        -  goenames bruker id')
    print('-i --input       -  full path eller relativ path')
    print('-o --output      -  full path eller relativ path')
    print('-f --format      -  navn på format man ønsker i output')
    print('\nMulige format:')
    print('full             -  vil gi disse feltene LatLong, Latitiude, Longitude, Land, Sted')
    print('min              -  vil gi disse feltene LatLong')
    print('\n')

def main(argv):
    input_filename = ''
    output_filename = 'output.csv'
    output_format = ''
    genonames_user = ''
    try:
        opts, args = getopt.getopt(argv,'hi:o:u:f:',['help', 'input=', 'output=', 'user=','format='])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-i", "--input"):
            input_filename = arg
        elif opt in ("-o", "--output"):
            output_filename = arg
        elif opt in ('-f', '--format'):
            output_format = arg
        elif opt in ('-u', '--user'):
            genonames_user = arg

    if input_filename == '':
        print(' - Inputfil ikke spesifisert, avslutter. Skriv "geoname_decoder.py -h" for hjelp')
        sys.exit()
    if genonames_user == '':
        print(' -  Ingen geonames bruker angitt, avslutter. Skriv "geoname_decoder.py -h" for hjelp')
        sys.exit()
    if output_filename == 'output.csv':
        print(' - Outputfil ikke spesifisert, skriver til output.csv')
    if output_format == '':
        print(' - Geocode format ikke spesifisert, skriver full format')



    with open(output_filename, 'w', encoding='utf-8') as output_file:
        write_header_to_file(output_file)
        with open(input_filename, 'r', encoding='utf-8') as input_file:
            already_decoded = dict()
            values_looked_up_online = 0
            values_found_in_cache = 0
            values_blank = 0
            values_not_found = 0
            input_file.readline()
            for line in input_file:
                if line == '' or line == None:
                    values_blank = values_blank + 1
                    continue
                if line in already_decoded:
                    decoded_values = already_decoded.get(line)
                    write_to_file(output_file, decoded_values)
                    values_found_in_cache = values_found_in_cache + 1
                else:
                    g = geocoder.geonames(line, method='details', key=genonames_user)
                    if not g.ok:
                        print("Fant ikke noe treff på linje " + 
                            str( 1 + values_blank + values_not_found + values_found_in_cache + values_looked_up_online) +
                            "; " + str(line))
                        values_not_found = values_not_found + 1
                    decoded_values = dict()
                    if g != None:
                        decoded_values['geonamesId'] = str(g.geonames_id) if g.geonames_id != None else '' 
                        decoded_values['Latitiude'] = str(g.lat) if g.lat != None else ''
                        decoded_values['Longitude'] = str(g.lng) if g.lng != None else ''
                        decoded_values['LatLong'] = decoded_values['Latitiude'] + ',' + decoded_values['Longitude']
                        decoded_values['Land'] = str(g.country) if g.country != None else ''
                        decoded_values['Sted'] = str(g.address) if g.address != None else ''
                    write_to_file(output_file, decoded_values)
                    already_decoded[line] = decoded_values
                    values_looked_up_online = values_looked_up_online + 1
    print('\n = Leste totalt ' + str(values_looked_up_online + values_found_in_cache + values_not_found + values_blank) + ' Linjer. Hvor:\n' +
        ' = ' + str(values_found_in_cache + values_looked_up_online) + ' geonames ble funnet\n' +
        ' = ' + str(values_looked_up_online) + ' er unike goenames ids i denne filen,\n' + 
        ' = ' + str(values_not_found) + ' geonames ikke ble funnet,\n' +
        ' = ' + str(values_blank) + ' linjer ikke inneholdt noen verdi.')
if __name__ == "__main__":
    main(sys.argv[1:])
