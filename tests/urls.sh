#/bin/sh
ab -n 10000 -c 20 -g 1.data http://localhost:8080/web/
ab -n 10000 -c 20 -g 2.data http://localhost:8080/web/index.html
ab -n 10000 -c 20 -g 3.data http://localhost:8080/web/about_us.html
ab -n 10000 -c 20 -g 4.data http://localhost:8080/web/mars.html
ab -n 10000 -c 20 -g 5.data http://localhost:8080/web/all_ids.html?page=5
ab -n 10000 -c 20 -g 6.data http://localhost:8080/web/2015.html
ab -n 10000 -c 20 -g 7.data http://localhost:8080/ws/IAU/0215
ab -n 10000 -c 20 -g 8.data http://localhost:8080/ws/IAU/2015
ab -n 10000 -c 20 -g 9.data http://localhost:8080/ws/IAU
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 1.data http://localhost:8080/web/'; set output '1.png'; plot '1.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 2.data http://localhost:8080/web/index.html'; set output '2.png'; plot '2.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 3.data http://localhost:8080/web/about_us.html'; set output '3.png'; plot '3.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 4.data http://localhost:8080/web/mars.html'; set output '4.png'; plot '4.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 5.data http://localhost:8080/web/all_ids.html?page=5'; set output '5.png'; plot '5.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 6.data http://localhost:8080/web/2015.html'; set output '6.png'; plot '6.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 7.data http://localhost:8080/web/IAU/0215'; set output '7.png'; plot '7.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 8.data http://localhost:8080/web/IAU/2015'; set output '8.png'; plot '8.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
gnuplot -e "set terminal png; set title 'ab -n 10000 -c 20 -g 9.data http://localhost:8080/web/IAU'; set output '9.png'; plot '9.data' using 9 smooth sbezier with lines title 'Response Time (ms)'"
