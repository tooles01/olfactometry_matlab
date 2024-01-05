%% Path Settings

% Directory of olfa_driver_object.py
python_env_folder_path = 'C:\Users\shann\Dropbox (NYU Langone Health)\Shannon_Dropbox\Duke odor calibration\New folder\';

%% Olfa Settings

% COM settings
COM_settings_mfc = py.dict();
COM_settings_mfc{'baudrate'} = 115200;
COM_settings_mfc{'com_port'} = 5;   % ** will need to be changed by user

% MFC config
MFC_settings = py.dict();
MFC_settings{'MFC_type'} = 'alicat_digital';
MFC_settings{'address'} = 'A';
MFC_settings{'arduino_port_num'} = 2;
MFC_settings{'capacity'} = 100;     % ** may need to be changed by user
MFC_settings{'gas'} = 'Air';
MFC_settings{'slave_index'} = 1;
