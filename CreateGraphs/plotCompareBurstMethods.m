%% 

opt_extra_opt = csvread('simdata11N=32k=2_burst_low_opt_servers+extra_opt_freq.csv');
opt_extra_min = csvread('simdata11N=32k=2_burst_low_opt_servers+extra_min_freq.csv');
opt_max = csvread('simdata11N=32k=2_burst_low_opt_servers-extra_max_freq.csv');
opt_opt = csvread('simdata11N=32k=2_burst_low.csv');

alpha = opt_extra_opt(1:end,2)';
beta = opt_extra_min(1:end,3)';

k = beta./alpha;

latency_opt_extra_opt = opt_extra_opt(1:end,end - 1)';
latency_opt_extra_min = opt_extra_min(1:end,end - 1)';
latency_opt_max = opt_max(1:end,end - 1)';
latency_opt_opt = opt_opt(1:end, end - 1)';

power_opt_extra_opt = opt_extra_opt(1:end,end)';
power_opt_extra_min = opt_extra_min(1:end,end)';
power_opt_max = opt_max(1:end,end)';
power_opt_opt = opt_opt(1:end, end)';

figure(1)
hold on
plot(beta, latency_opt_extra_opt, 'k')
plot(beta, latency_opt_extra_min, 'm')
plot(beta, latency_opt_max, 'b')
plot(beta, latency_opt_opt, 'r')

title('Tail Latency for Low Arrival Rate (11,000 req/s)')
xlabel('beta')
ylabel('P(T>D_0)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off

figure(2)
hold on
plot(beta, power_opt_extra_opt, 'k')
plot(beta, power_opt_extra_min, 'm')
plot(beta, power_opt_max, 'b')
plot(beta, power_opt_opt', 'r')

title('Power Usage for Low Arrival Rate (11,000 req/s)')
xlabel('beta')
ylabel('Power (W)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off

%%

opt_extra_opt = csvread('simdata11N=32k=2_burst_med_opt_servers+extra_opt_freq.csv');
opt_extra_min = csvread('simdata11N=32k=2_burst_med_opt_servers+extra_min_freq.csv');
opt_max = csvread('simdata11N=32k=2_burst_med_opt_servers-extra_max_freq.csv');
opt_opt = csvread('simdata11N=32k=2_burst_med.csv');

alpha = opt_extra_opt(1:end,2)';
beta = opt_extra_min(1:end,3)';

k = beta./alpha;

latency_opt_extra_opt = opt_extra_opt(1:end,end - 1)';
latency_opt_extra_min = opt_extra_min(1:end,end - 1)';
latency_opt_max = opt_max(1:end,end - 1)';
latency_opt_opt = opt_opt(1:end, end - 1)';

power_opt_extra_opt = opt_extra_opt(1:end,end)';
power_opt_extra_min = opt_extra_min(1:end,end)';
power_opt_max = opt_max(1:end,end)';
power_opt_opt = opt_opt(1:end, end)';

figure(1)
hold on
plot(beta, latency_opt_extra_opt, 'k')
plot(beta, latency_opt_extra_min, 'm')
plot(beta, latency_opt_max, 'b')
plot(beta, latency_opt_opt, 'r')

title('Tail Latency for Med Arrival Rate (41,000 req/s)')
xlabel('beta')
ylabel('P(T>D_0)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off

figure(2)
hold on
plot(beta, power_opt_extra_opt, 'k')
plot(beta, power_opt_extra_min, 'm')
plot(beta, power_opt_max, 'b')
plot(beta, power_opt_opt', 'r')

title('Power Usage for Med Arrival Rate (41,000 req/s)')
xlabel('beta')
ylabel('Power (W)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off

%%

opt_extra_opt = csvread('simdata11N=32k=2_burst_high_opt_servers+extra_opt_freq.csv');
opt_extra_min = csvread('simdata11N=32k=2_burst_high_opt_servers+extra_min_freq.csv');
opt_max = csvread('simdata11N=32k=2_burst_high_opt_servers-extra_max_freq.csv');
opt_opt = csvread('simdata11N=32k=2_burst_high.csv');

alpha = opt_extra_opt(1:end,2)';
beta = opt_extra_min(1:end,3)';

k = beta./alpha;

latency_opt_extra_opt = opt_extra_opt(1:end,end - 1)';
latency_opt_extra_min = opt_extra_min(1:end,end - 1)';
latency_opt_max = opt_max(1:end,end - 1)';
latency_opt_opt = opt_opt(1:end, end - 1)';

power_opt_extra_opt = opt_extra_opt(1:end,end)';
power_opt_extra_min = opt_extra_min(1:end,end)';
power_opt_max = opt_max(1:end,end)';
power_opt_opt = opt_opt(1:end, end)';

figure(1)
hold on
plot(beta, latency_opt_extra_opt, 'k')
plot(beta, latency_opt_extra_min, 'm')
plot(beta, latency_opt_max, 'b')
plot(beta, latency_opt_opt, 'r')

title('Tail Latency for High Arrival Rate (71,000 req/s)')
xlabel('beta')
ylabel('P(T>D_0)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off

figure(2)
hold on
plot(beta, power_opt_extra_opt, 'k')
plot(beta, power_opt_extra_min, 'm')
plot(beta, power_opt_max, 'b')
plot(beta, power_opt_opt', 'r')

title('Power Usage for High Arrival Rate (71,000 req/s)')
xlabel('beta')
ylabel('Power (W)')
legend('Optimal Servers + Extra w/ Opt Freq', 'Optimal Servers + Extra w/ Min Freq', 'Optimal Servers w/ Max Freq', 'Optimal Servers w/ Opt Freq')
hold off
