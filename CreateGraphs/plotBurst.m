burst_low = csvread('simdata11N=32k=2_burst_low.csv');
burst_med = csvread('simdata11N=32k=2_burst_med.csv');
burst_high = csvread('simdata11N=32k=2_burst_high.csv');

alpha = burst_low(:,2)';
beta = burst_low(:,3)';

k = beta./alpha;

burst_low_power = burst_low(:,end)';
burst_med_power = burst_med(:,end)';
burst_high_power = burst_high(:,end)';

burst_low_latency = burst_low(:,end - 1)';
burst_med_latency = burst_med(:,end - 1)';
burst_high_latency = burst_high(:,end - 1)';

compute_low = burst_low(:,6)';
wake_up_low = burst_low(:,7)';
sleep_low = burst_low(:,8)';

compute_med = burst_med(:,6)';
wake_up_med = burst_med(:,7)';
sleep_med = burst_med(:,8)';

compute_high = burst_high(:,6)';
wake_up_high = burst_high(:,7)';
sleep_high = burst_high(:,8)';

figure(1)
hold on
plot(beta, burst_low_latency, 'k')
plot(beta, burst_med_latency, 'r')
plot(beta, burst_high_latency, 'm')

title('Tail Latency with Traffic Burst')
xlabel('beta')
ylabel('P(T>D_0)')
legend('Low Arrival Rate (11,000 req/s)', 'Med Arrival Rate (41,000 req/s)', 'High Arrival Rate (71,000 req/s)')
hold off

figure(2)
hold on
plot(beta, compute_low, 'k')
plot(beta, compute_med, 'r')
plot(beta, compute_high, 'm')

title('Utilization Rate with Traffic Burst')
xlabel('beta')
ylabel('Percentage')
legend('Low Arrival Rate (11,000 req/s)', 'Med Arrival Rate (41,000 req/s)', 'High Arrival Rate (71,000 req/s)')
hold off

figure(3)
hold on
plot(beta, burst_low_power, 'k')
plot(beta, burst_med_power, 'r')
plot(beta, burst_high_power, 'm')

title('Power Usage with Traffic Burst')
xlabel('beta')
ylabel('Percentage')
legend('Low Arrival Rate (11,000 req/s)', 'Med Arrival Rate (41,000 req/s)', 'High Arrival Rate (71,000 req/s)')
hold off
