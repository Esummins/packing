set -e
L=../logs
done1(){ grep -q "DONE\|ABORT\|Traceback" $L/$1.stdout 2>/dev/null; }
until done1 n061 && done1 n065 && done1 n074; do sleep 10; done
echo "batch1 complete"
for t in n095 n100; do python twofield.py --tag $t > $L/$t.stdout 2>&1 & done
wait
echo "batch2 complete"
for t in k1 k2; do python twofield.py --tag $t > $L/$t.stdout 2>&1 & done
wait
echo "batch3 complete"
python twofield.py --aggregate
