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

% The following is directory to save the output file
save_folder = 'mat_files/';

% Get a list of all files and folders in this folder.
files = dir(main_folder);
% Get a logical vector that tells which is a directory.
dirFlags = [files.isdir];
% Extract only those that are directories.
subFolders = files(dirFlags);
% Print folder names to command window.


for k = 3 : length(subFolders)
    
    % The following is the folder for the experiment
    exp_name = subFolders(k).name;
    %if exp_name == '9'
    %    a = 1
    %end
    fprintf('Sub folder #%d = %s\n', k, exp_name);

    % The folder where the traces are saved
    exp_folder = strcat(main_folder, exp_name, '/');
    dir_name = strcat(exp_folder, '*.txt');
    % All the files in the directory which are in format of *.txt
    files = dir(dir_name);    
    
    % The maximum number of traces is 150k and counts keep track of errors
    % happening during the trace extraction
    RESULT = zeros(150000,1);
    CORRECT = {};
    count1 = 0;
    count2 = 0;
    count3 = 0;
    count4 = 0;

    l1 = zeros(20,1);
    l2 = zeros(20,1);
    l3 = zeros(20,1);
    
    idx = 1;
    % For each trace file in the traces directory 
    for file = files'

        % Get the file name and append it to folder dir to get the file dir
        f_name = strcat(exp_folder, file.name);

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

        %l1(idx) = sum(data(1:end,1));
        %l2(idx) = sum(data(1:end,2));
        %l3(idx) = sum(data(1:end,3));
        
        % We hit either the first monitored line or second monitored line, then
        % we do AND of a with shifted version of a, by doing this we make sure
        % we don't count the two consecutive hits because they are super close
        % and we save the result in b which is the clean version of data and we
        % just count the number of 1 in the b
        
        a1 = ( data(:,1) | data(:,2)  )';
       
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

        %gaps = diff(idxs); gap_val = max(gaps);

        RESULT(idx) = res1;
        
        if mod(idx, 1000) == 1
            idx
        end
        
        idx = idx + 1;
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
    
    %min1 = min(l1(1:idx))
    %max1 = max(l1(1:idx))
    %min2 = min(l2(1:idx))
    %max2 = max(l2(1:idx))
    %min3 = min(l3(1:idx))
    %max3 = max(l3(1:idx))
    %idx    
    
end

RES2 = RES;
RES2(RES2 < noise_thresh) = 0;
[vals, Volumes] = findpeaks(RES);


