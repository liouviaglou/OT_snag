import sys
import configparser 

# python3 configparser_test.py credentials.txt

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    print (config['signup']['firstName'])
    print (config['signup']['lastName'])
