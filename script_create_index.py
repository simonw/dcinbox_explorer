import schema
import es_connection

if __name__ == '__main__':
    print "Creating index"
    print schema.Email.init()
