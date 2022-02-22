criteria=$1

for i in $( ls -d -1 $criteria/* );
do
	src=$i
	echo "<DOCS>" > tmp
	cat $i >> tmp
	echo "</DOCS>" >> tmp
	mv tmp xml/$i.xml
	echo $i.xml
done
