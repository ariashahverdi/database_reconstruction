clc; 
clear;

% After Parsing traces the final plot for potential 
% Volumes is noisy. Take a look at RES and decide 
% how does the figure look like and set is appropriately
% For mine it was around 2,3
noise_thresh = 2;

% Threshold for whether a certain timing measurement is hit or miss
% Values less than this is considered to be a hit
thresh = 100;

% The following folder contains all the measurement for different
% experiments
main_folder = 'Traces/';
%main_folder = '/mnt/data/nis2008_2_new/';

% The following is directory to save the output file
save_folder = 'mat_files/';

% The maximum number of traces is 150k and counts keep track of errors
% happening during the trace extraction
RESULT = zeros(150000,1);
CORRECT = {};
count1 = 0;
count2 = 0;
count3 = 0;
count4 = 0;

idx = 1;

fileNameFormat = '%str%d.txt';

% Just a mapping from ranges to numbers
ranges = ...
struct(	'r1_1',0, 'r1_2',1, 'r1_3',2, 'r1_4',3, 'r1_5',4, 'r1_6',5, 'r1_7',6, 'r1_8',7, 'r1_9',8, 'r1_10',9, 'r1_11',10, 'r1_12',11, ...
		'r2_2',12, 'r2_3',13, 'r2_4',14, 'r2_5',15, 'r2_6',16, 'r2_7',17, 'r2_8',18, 'r2_9',19, 'r2_10',20, 'r2_11',21, 'r2_12',22, ...
		'r3_3',23, 'r3_4',24, 'r3_5',25, 'r3_6',26, 'r3_7',27, 'r3_8',28, 'r3_9',29, 'r3_10',30, 'r3_11',31, 'r3_12',32, ...
		'r4_4',33, 'r4_5',34, 'r4_6',35, 'r4_7',36, 'r4_8',37, 'r4_9',38, 'r4_10',39, 'r4_11',40, 'r4_12',41, ...
		'r5_5',42, 'r5_6',43, 'r5_7',44, 'r5_8',45, 'r5_9',46, 'r5_10',47, 'r5_11',48, 'r5_12',49, ...
		'r6_6',50, 'r6_7',51, 'r6_8',52, 'r6_9',53, 'r6_10',54, 'r6_11',55, 'r6_12',56, ...
		'r7_7',57, 'r7_8',58, 'r7_9',59, 'r7_10',60, 'r7_11',61, 'r7_12',62, ...
		'r8_8',63, 'r8_9',64, 'r8_10',65, 'r8_11',66, 'r8_12',67, ...
		'r9_9',68, 'r9_10',69, 'r9_11',70, 'r9_12',71, ...
		'r10_10',72, 'r10_11',73, 'r10_12',74, ...
		'r11_11',75, 'r11_12',76, ...
		'r12_12',77);

% All possible ranges
all_ranges = ["r1_1", "r1_2", "r1_3", "r1_4", "r1_5", "r1_6", "r1_7", "r1_8", "r1_9", "r1_10", "r1_11", "r1_12", "r2_2", "r2_3", "r2_4", "r2_5", "r2_6", "r2_7", "r2_8", "r2_9", "r2_10", "r2_11", "r2_12", "r3_3", "r3_4", "r3_5", "r3_6", "r3_7", "r3_8", "r3_9", "r3_10", "r3_11", "r3_12", "r4_4", "r4_5", "r4_6", "r4_7", "r4_8", "r4_9", "r4_10", "r4_11", "r4_12", "r5_5", "r5_6", "r5_7", "r5_8", "r5_9", "r5_10", "r5_11", "r5_12", "r6_6", "r6_7", "r6_8", "r6_9", "r6_10", "r6_11", "r6_12", "r7_7", "r7_8", "r7_9", "r7_10", "r7_11", "r7_12", "r8_8", "r8_9", "r8_10", "r8_11", "r8_12", "r9_9", "r9_10", "r9_11", "r9_12", "r10_10", "r10_11", "r10_12", "r11_11", "r11_12", "r12_12"];


exp_name = 'only1diffhigh_nis2008_4';
%exp_name = '1diff2diffhigh_nis2008_4';
%exp_name = 'everyotherhigh_nis2008_4';

% Only the queries in the form [i,i+1] are high
%exp1
high_query = ["r1_2" , "r2_3", "r3_4", "r4_5", "r5_6", "r6_7", "r7_8", "r8_9", "r9_10", "r10_11","r11_12" ];

% Queries in the form [i,i+1] and [i,i+2] are high
%exp2
%high_query = ["r1_2" , "r2_3", "r3_4", "r4_5", "r5_6", "r6_7", "r7_8", "r8_9", "r9_10", "r10_11","r11_12",...
%              "r1_3", "r2_4", "r3_5", "r4_6", "r5_7", "r6_8", "r7_9", "r8_10", "r9_11", "r10_12" ];

% Depending on the nis_db the queires are high-low-high-low...
% So it means you have to first find the ordered query list and
% alternate over them

%exp3_1
%high_query = ["r11_11", "r8_8", "r5_5", "r12_12", "r10_10", "r1_1", "r10_11", "r6_7", "r7_8", "r4_5", "r3_4",...
%              "r9_11", "r10_12", "r4_6", "r8_10", "r2_4", "r8_11", "r9_12", "r4_7", "r7_10", "r1_4", ...
%              "r7_11", "r6_10", "r2_6", "r1_5", "r7_12", "r3_8", "r1_6", "r6_12", "r3_9", "r1_7", ...
%              "r4_11", "r3_10", "r4_12", "r2_10", "r2_11", "r1_10", "r1_11"];

%exp3_2
%high_query = ["r11_11", "r6_6", "r10_10", "r12_12", "r7_7", "r3_3", "r10_11", "r8_9", "r9_10", "r6_7", "r3_4",...
%              "r1_2", "r10_12", "r6_8", "r4_6", "r3_5", "r1_3", "r9_12", "r7_10", "r4_7", "r2_5", ...
%              "r8_12", "r6_10", "r4_8", "r2_6", "r6_11", "r5_10", "r3_8", "r1_6", "r6_12", "r3_9", ...
%              "r1_7", "r4_11", "r2_9", "r4_12", "r2_10", "r3_12", "r1_10", "r1_11"];

%exp3_3
%high_query = ["r11_11", "r12_12", "r9_9", "r2_2", "r8_8", "r3_3", "r11_12", "r5_6", "r4_5", "r8_9", "r2_3",...
%              "r1_2", "r9_11", "r5_7", "r3_5", "r2_4", "r1_3", "r8_11", "r3_6", "r6_9", "r7_10", ...
%              "r8_12", "r2_6", "r4_8", "r6_10", "r6_11", "r4_9", "r2_7", "r1_6", "r5_11", "r3_9", ...
%              "r1_7", "r4_11", "r3_10", "r4_12", "r2_10", "r3_12", "r1_10", "r1_11"];
          
%exp3_4
%high_query = ["r11_11", "r8_8", "r4_4", "r10_10", "r5_5", "r3_3", "r11_12", "r8_9", "r5_6", "r9_10", "r3_4",...
%              "r1_2", "r6_8", "r8_10", "r4_6", "r3_5", "r1_3", "r6_9", "r5_8", "r4_7", "r2_5", ...
%              "r8_12", "r6_10", "r4_8", "r2_6", "r6_11", "r4_9", "r3_8", "r1_6", "r5_11", "r3_9", ...
%              "r1_7", "r5_12", "r2_9", "r4_12", "r2_10", "r3_12", "r1_10", "r1_11"];

% exp3_10
%high_query = ["r11_11" , "r8_8", "r9_9", "r4_4", "r2_2", "r3_3", "r11_12", "r5_6", "r4_5", "r7_8","r3_4",...
%              "r1_2", "r10_12", "r6_8", "r8_10", "r3_5", "r1_3", "r9_12", "r6_9", "r3_6", "r2_5", ...
%              "r8_12", "r5_9", "r6_10", "r3_7", "r6_11", "r4_9", "r3_8", "r1_6", "r6_12", "r3_9", ...
%              "r1_7", "r4_11", "r2_9", "r4_12", "r2_10", "r3_12", "r1_10", "r1_11"];


% All the rest are queries which are exectured half of the times
low_query = setdiff(all_ranges, high_query);


% For each trace file in the traces directory 
for q_idx=1:size(all_ranges,2)
    query = all_ranges(q_idx)
    
    if ismember(query, high_query)
        higher_bound = 200;
    else
        higher_bound = 100;
    end
    
    for f_idx = 1:higher_bound
        
        f_val = ranges.(query) * 200 + f_idx;
        % Get the file name and append it to folder dir to get the file dir
        f_name = sprintf(fileNameFormat, main_folder, f_val);
        %f_name = strcat(exp_folder, file.name)

        % Load File From Directory
        data_orig = load(f_name);

        % If the timing measurement is more than 1000 we set it to 1000 because
        % it is off anyway, it makes plotting the value better
        data_orig(data_orig>300) = 300;

        % if size of the measurement is less than 100, it is for sure not a 
        % proper traces as the trace should have at least 500 points because
        % we set the Mastik to recored at least 500 sample points
        % Note: This error does not hapaaeepen much often
        if (size(data_orig,1) <= 100)
            count1 = count1 + 1;
            continue; 
        end

        % If the last 100 sample points in data has more than 5 zeros we don't
        % accept this trace, although the last 100 point doesn't have
        % information about hit or misses we drop them anyway
        if nnz(~data_orig(end-100:end)) > 5 
            count2 = count2 + 1; 
            continue; 
        end

        % We save the data_orig in the data array and set the values which are
        % greater than threshold to 0 as they are cache miss. Then we count how
        % many zero element we have in the data, the number of zeros represents
        % how many samples we missed during the measurement. We then set the
        % hit values to 1
        data = data_orig;
        zero_count = nnz(~data);
        data(data > thresh) = 0; 
        data(data ~= 0) = 1;

        % We hit either the first monitored line or second monitored line, then
        % we do AND of a with shifted version of a, by doing this we make sure
        % we don't count the two consecutive hits because they are super close
        % and we save the result in b which is the clean version of data and we
        % just count the number of 1 in the b
        
        a1 = ( data(:,1) | data(:,2)  )';
        %a1 = data(:,1)';
       
        % This line is very important to reduce the noise, you can uncomment it
        % and see the reuslt
        aa1 = a1 & ~([a1(2:end) 1]) & ~([a1(3:end) 1 1]) & ~([a1(4:end) 1 1 1]);
        b1 = aa1;
        res1 = sum(b1);

        % We check the indexes of elements where they are 1, if the list is
        % empty it means that the trace was empty and there was no hit in it,
        % so we drop that trace as well
        idxs = find(b1==1);
        if isempty(idxs) 
            count3 = count3 + 1; 
            continue; 
        end

        RESULT(idx) = res1;
        
        idx = idx + 1;        
    end

end
    
% We drop the zero elements as we have an assumption that the measurements
% are not zero
RESULT(RESULT==0) = [];
unique(RESULT);
len_db = 100000;
RES = zeros(len_db+5,1);
for i=1:len_db+5
    RES(i) = sum(RESULT==(i));
end

workspace_file = strcat( save_folder, exp_name );
save(workspace_file);

score_file = strcat( save_folder, 'scores/', exp_name, '.txt' );
fid = fopen(score_file,'wt');
A = RES;
for ii = 1:size(A,1)
    fprintf(fid,'%g',A(ii,:));
    fprintf(fid,'\n');
end
fclose(fid);
    
%save(score_file, 'RES');
% Print the number of error from each category
fprintf('count1 error : %d \n', count1);
fprintf('count2 error = %d \n', count2);
fprintf('count3 error = %d \n', count3);

RES2 = RES;
RES2(RES2 < noise_thresh) = 0;
[vals, Volumes] = findpeaks(RES);
