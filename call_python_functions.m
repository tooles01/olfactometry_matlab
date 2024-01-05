%% call_python_functions
% Call python olfactometry functions from MATLAB


%%
clear variables
clear classes %#ok<CLCLS>       % unload modules

%% Load config variables
load_config;

%% Add python module to path
addpath(python_env_folder_path);                % Add to matlab path
append(py.sys.path, python_env_folder_path);    % Add to python path

%% Load python module
module_name = 'olfa_driver_object';
mod_obj = py.importlib.import_module(module_name);  % import module
py.importlib.reload(mod_obj);                       % reload module

%% Olfactometer
olfa_object = py.olfa_driver_object.TeensyOlfa(MFC_settings);   % Create olfactometer object
olfa_object.connect_olfa(COM_settings_mfc);                     % Connect to Teensy

%% Set MFC
flow_value = 90;
olfa_object.set_flowrate(flow_value);

%% Open/close odor vial
vial_number = 6;
duration_open = 5;

olfa_object.set_valveset(vial_number, 1);   % Open odor vial
pause(duration_open);                       % Pause
olfa_object.set_valveset(vial_number, 0);   % Close odor vial
