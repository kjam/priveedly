while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -t|--type)
    BACKUP_TYPE="$2"
    shift # past argument
    ;;
esac
shift # past argument or value
done

source /home/YOUR_USER/.profile

if [[ -n $BACKUP_TYPE ]]
then
    PGPASSWORD=CHANGE_TO_YOUR_PASSWORD pg_dump -U CHANGE_TO_YOUR_USER -p 5433 DB_NAME > /tmp/priveedly.sql
    /usr/bin/aws s3 cp /tmp/priveedly.sql s3://YOUR_BACKUP_LOCATION/"$BACKUP_TYPE"/
fi
