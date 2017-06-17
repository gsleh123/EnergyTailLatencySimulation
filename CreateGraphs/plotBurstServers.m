burst_low = csvread('simdata11N=32k=2_burst_low_opt_servers+extra_opt_freq.csv');
burst_med = csvread('simdata11N=32k=2_burst_med_opt_servers+extra_opt_freq.csv');
burst_high = csvread('simdata11N=32k=2_burst_high_opt_servers+extra_opt_freq.csv');

alpha = burst_low(1:end,2)';
beta = burst_low(1:end,3)';

k = beta./alpha;

burst_low_latency = burst_low(1:end,end - 1)';
burst_med_latency = burst_med(1:end,end - 1)';
burst_high_latency = burst_high(1:end,end - 1)';

servers_low = burst_low(1:end,4)';
servers_med = burst_med(1:end,4)';
servers_high = burst_high(1:end,4)';

servers_low = servers_low - burst_low(1, 4);
servers_med = servers_med - burst_med(1, 4);
servers_high = servers_high - burst_high(1, 4);

figure(1)
hold on
plot(beta, burst_low_latency, 'k')
plot(beta, burst_med_latency, 'r')
plot(beta, burst_high_latency, 'm')

title('Tail Latency')
xlabel('beta')
ylabel('P(T>D_0)')
legend('Low Arrival Rate (11,000 req/s)', 'Med Arrival Rate (41,000 req/s)', 'High Arrival Rate (71,000 req/s)')
hold off

figure(2)
hold on
plot(beta, servers_low, 'k')
plot(beta, servers_med, 'r')
plot(beta, servers_high, 'm')

title('Extra Servers to Satisfy Tail Latency')
xlabel('beta')
ylabel('Num of Servers')
legend('Low Arrival Rate (11,000 req/s)', 'Med Arrival Rate (41,000 req/s)', 'High Arrival Rate (71,000 req/s)')
hold off

