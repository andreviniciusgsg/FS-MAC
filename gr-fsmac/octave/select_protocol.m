function [out] = select_protocol(file_name, curr_prot, curr_y)

# select_protocol(file_name, curr_prot, curr_y) returns the index of the best protocol to use as well as the expected maximization value.
# Inputs: 
#	- file_name: Input file with data. By default, 1st column represents the protocol id and 2nd column the maximization parameter.
# 	- curr_prot: Current protocol id in use.
#	- curr_y: Current value of maximization parameter.
# Outputs:
# 	- p: Index of best protocol
# 	- v: Value of maximization parameter. This is related to the 2nd columns on input file.
#
# Author: André Gomes, andre.gomes@dcc.ufmg.br - Federal University of Minas Gerais (UFMG), Brazil.
# 28/11/2017
#

##### Closes all open windows on octave #####

close all;

##### Set environment for MACOS #####

	setenv("GNUTERM", "qt");

##### Parse results #####

	data = dlmread(file_name);

	protocol1 = data(find(data(:,1) == 1),:);
	protocol2 = data(find(data(:,1) == 2),:);

##### Linear Regression #####
	options = optimset('GradObj', 'on', 'MaxIter', '1000');

	x1 = protocol1(:, 3:size(protocol1, 2));
	[x1, u1, s1] = feature_scaling(x1);
	x2 = protocol2(:, 3:size(protocol2, 2));
	[x2, u2, s2] = feature_scaling(x2);

	y1 = protocol1(:, 2);
	y2 = protocol2(:, 2);

	theta1 = calculate_theta(x1, y1);
	theta2 = calculate_theta(x2, y2);

	hypothesis1 = [ones(size(x1, 1), 1) x1]*theta1;
	err1 = mean(abs(hypothesis1 - y1));
	hypothesis2 = [ones(size(x2, 1), 1) x2]*theta2;
	err2 = mean(abs(hypothesis2 - y2));

##### Get best protocol #####
	curr_x = data(size(data, 1), 3:size(data, 2));

	## Calculating hypothesis for current input ##
	if curr_prot == 1
		#v1 = hypothesis1(size(hypothesis1, 1));
		v1 = curr_y;
		curr_x = (curr_x - u2)/s2; # Feature scaling according to previus mean and (vmax - vmin)
		v2 = [1 curr_x]*theta2;
	else
		#v2 = hypothesis2(size(hypothesis2, 1));
		v2 = curr_y;
		curr_x = (curr_x - u1)/s1; # Feature scaling according to previus mean and (vmax - vmin)
		v1 = [1 curr_x]*theta1;
	endif 

	out = zeros(1, 3);
	## Best protocol ##
	if v1 > v2
		p = 1;
		v = v1;
	else
		p = 2;
		v = v2;
	endif

	diff = abs(v1 - v2);

	#out = [p v diff];
	out = p;

	printf("Avg err1 = %f, avg err2 = %f, diff = %f\n", err1, err2, diff);

endfunction