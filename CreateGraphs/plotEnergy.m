opt_opt = csvread('simdata11N=32k=2.csv');
min_opt = csvread('simdata21N=32k=2.csv');
min_max = csvread('simdata22N=32k=2.csv');
max_opt = csvread('simdata31N=32k=2.csv');
max_max = csvread('simdata32N=32k=2.csv');

arr_rate = opt_opt(:,1)';

opt_opt_power = opt_opt(:,end)';
min_opt_power = min_opt(:,end)';
min_max_power = min_max(:,end)';
max_opt_power = max_opt(:,end)';
max_max_power = max_max(:,end)';

opt_opt_latency = opt_opt(:,end - 1)';
min_opt_latency = min_opt(:,end - 1)';
min_max_latency = min_max(:,end - 1)';
max_opt_latency = max_opt(:,end - 1)';
max_max_latency = max_max(:,end - 1)';

figure(1)
hold on
plot(arr_rate, opt_opt_power, 'k')
plot(arr_rate, max_max_power, 'r')
plot(arr_rate, min_max_power, 'm')
plot(arr_rate, max_opt_power, 'b')
plot(arr_rate, min_opt_power, 'c')

title('Power Usage')
xlabel('Total traffic {\lambda} (requests/s)')
ylabel('Total power consumption (W)')
legend('Opt Servers + Opt Freq', 'All Servers + Max Freq', 'Min Servers + Max Freq', 'All Servers + Opt Freq', 'Min Servers + Opt Freq')
hold off

figure(2)
hold on
plot(arr_rate, opt_opt_latency, 'k')
plot(arr_rate, max_max_latency, 'r')
plot(arr_rate, min_max_latency, 'm')
plot(arr_rate, max_opt_latency, 'b')
plot(arr_rate, min_opt_latency, 'c')

title('Tail Latency')
xlabel('Total traffic {\lambda} (requests/s)')
ylabel('P(T>D_0)')
legend('Opt Servers + Opt Freq', 'All Servers + Max Freq', 'Min Servers + Max Freq', 'All Servers + Opt Freq', 'Min Servers + Opt Freq')
hold off
