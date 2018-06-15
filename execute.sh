#!/bin/bash
# Controls the maximum of threads that will be created.
MAX_THREADS=1

FILENAME="data/ratings_100000.csv"

SIMILARITIES=("0")
SIMILARITIESCODES=('cn')

SIMILARITIESCONTRACT=("0")
SIMILARITIESCONTRACTCODES=('cn')


CONTRACTS=("0" "1")
CONTRACTSCODES=('greedy' 'randgreedy')

LAYERS=(0 1 2)
LAYERSCODES=('01' '0' '1')
LAYERSFILESCODES=('2layers' 'userlayer' 'itemlayer')

LEVELS=("0" "1" "2" "3" "4" "5")

TOEXECUTE=$((${#LAYERS[@]}*${#CONTRACTS[@]}*${#SIMILARITIESCONTRACT[@]}*${#SIMILARITIES[@]}*${#LEVELS[@]}))
EXECUTED=0
# Executes the python scripts.
# For each layer.
for i in $(seq 0 $((${#LAYERS[@]}-1)))
do
    # For contraction method.
    for j in $(seq 0 $((${#CONTRACTS[@]}-1)))
    do
        # For each similarity used for contract.
        for m in $(seq 0 $((${#SIMILARITIESCONTRACT[@]}-1)))
        do
            # For each similarity in the similarities array.
            for k in $(seq 0 $((${#SIMILARITIES[@]}-1)))
            do
                # For each level of coarsening.
                for l in $(seq 0 $((${#LEVELS[@]}-1)))
                do
                    OUTPUTFILE="output/${LAYERSFILESCODES[$i]}/${CONTRACTSCODES[$j]}_${SIMILARITIESCONTRACTCODES[$m]}_${SIMILARITIESCODES[$k]}_${LEVELS[$l]}.csv"
                    echo "python main.py -f "$FILENAME" -m ${LEVELS[$l]} -o "$OUTPUTFILE" -c ${CONTRACTS[$j]} -cm ${SIMILARITIESCONTRACT[$m]} -s ${SIMILARITIES[$k]} -ls "${LAYERSCODES[$i]}" &"
                    python main.py -f "$FILENAME" -m ${LEVELS[$l]} -o "$OUTPUTFILE" -c ${CONTRACTS[$j]} -cm ${SIMILARITIESCONTRACT[$m]} -s ${SIMILARITIES[$k]} -ls "${LAYERSCODES[$i]}" &
                    EXECUTED=$(($EXECUTED+1))
                    echo "("$EXECUTED"/"$TOEXECUTE")"
                    echo "--------------------------"
                    while [ $( jobs | wc -l ) -ge "$MAX_THREADS" ]; do
                        sleep 0.1
                    done
                done
            done
        done
    done
done
