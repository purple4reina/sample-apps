#!/usr/bin/env sh

alias timeit="date +%s%N"

bench() {
    cmd=$1

    iters=100000
    total=0
    for ((i=1;i<=$iters; i++))
    do
        start=`timeit`
        $cmd > /dev/null
        end=`timeit`
        total=$(($total+$(($end-$start))))
    done

    echo $(($total/$iters))
}

echo "bench no"
before=`bench ./ddtraceNo`
echo "bench yes"
after=`bench ./ddtraceYes`

echo "Before: $before"
echo "After:  $after"
echo "Diff:   $(($after-$before))"
