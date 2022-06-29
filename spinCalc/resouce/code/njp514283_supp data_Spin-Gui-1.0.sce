////////////////////////////////////////////////////////////////////////////////
//
//    Spin-Gui-1.0.sce
//
//    Stuttgart, 29/12/14
//
//    (C) Markus Ternes
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
////////////////////////////////////////////////////////////////////////////////

clear();
clearglobal();
PATH=get_absolute_file_path('Spin-Gui-1.0.sce');

helperfile="Spin-Hamiltonians-1.0.sce";
ierr=execstr('exec(PATH+helperfile,-1)','errcatch');  //load some usefull functions
if ierr<>0 then disp('file '+helperfile+' missing!'); abort;
end

helperfile="Spin-additional-functions-1.0.sce"; 
ierr=execstr('exec(PATH+helperfile,-1)','errcatch');  //load some usefull functions
if ierr<>0 then disp('file '+helperfile+' missing!'); abort;
end

helperfile="Spin-fit-functions-1.0.sce";
ierr=execstr('exec(PATH+helperfile,-1)','errcatch');  //load some usefull functions
if ierr<>0 then disp('file '+helperfile+' missing! Fitting disabled'); 
end

c = get(0);
ierr=execstr('set(c, ''UseDeprecatedSkin'', ''on'')','errcatch'); //for version 5.5.0 only

global PATH

global %savedata;
global %plotspec;
global %precission;
global %normalize;
global %zeroadj;
global %stopcalc;

global %Data        //experimental Data
global %Data_trunc  //experimental truncated Data
global Data_fname   //experimental Data filename
global calc         //calculated results
global old_k;       //old fitting parameters
global itcount;     //fitting iteration counter
global minvalues1;  //minium of slider and fit range
global maxvalues1;  //maxium of slider and fit range
global labels1;     //Slider lables 
//global winId;

global guicheckbox1; 
global guientry1; 
global guislider1;
global gui;
global f g h gh;   //graphic handles

clear("experiment");
clear("experiment2");

global experiment;
global experiment2;

global chk_exit;

stacksize('max');

// define an atom

atomlink.S=0.5;
atomlink.g=2;
atomlink.D=0;
atomlink.E=0;
atomlink.J=-0.04;
atomlink.U=0;
atomlink.w=20;

//define the experiment

experiment.T=1*0.08617;
experiment.xrange=10;
experiment.lt=0.005;
experiment.ptip=[0.0 0.0 0.0];
experiment.psample=[0 0 0];
experiment.atom=atomlink;
experiment.Eigenvec=[];
experiment.Eigenval=[];
experiment.position=1;
experiment.jposition=1;
experiment.A=1;
experiment.b=0;
experiment.x0=0;
experiment.y0=0;
experiment.B=[0 0 4];
experiment.matrix='1';
experiment.matrixDM='0, 0, 0';
experiment.heisenberg_coupling=0;
experiment.sample_entanglement=%T;
experiment.sef=1;
experiment.paramagnetic=%F;
experiment.paramag_S=5/2;
experiment.paramag_g=2;
experiment.eta=0.3;
experiment.no_eval=1000;
experiment.max_no_eigenstates=50;
experiment.third_order_calc=%T;
experiment.rate_calc=%F;
experiment.entanglement=%F;
experiment.allatomsequ=0;

calc.spec = [];
calc.states= [];
calc.occ = [];
calc.lifetime = [];
calc.entropy = [];
calc.giantspin= [];
calc.negativity= [];
calc.spec_raw=[];

experiment2=experiment;

%savedata =%F; 
// If %savedata = %T all intermediate calculated data is saved
// The files are saved in the standart directory
// and contain files like: 
// data_(in)_(mid)_(fin).dat for 3rd order (normal order)
// data_(in)_(mid)_(fin)r.dat for 3rd order (reversed order)
// data_(in)_(fin)SF.dat for 2nd order processes;
%plotspec =%F;
// if %plotspec = %F then all intermediate states are plotted
%precission=0.001;
// %precission sets the mininal (in) state occupation to be calculated
// and the minimal matrix element to be evaluated
// the calculation speed drastically depends on that value

%normalize=%F;
// all spectra are normalized to 'one' at high voltage

%zeroadj=%T;
// the ground state is set to zero when plotting states

%stopcalc=%F;

// build the gui:

f=figure('figure_position',[0,0],'figure_size',[1000,700],'auto_resize',..
'on','background',[33],'figure_name',..
'3rd order tunneling simulator. (c) 2010-2014 Markus Ternes, Version 1.0',..
'closerequestfcn',"gui_exit()");
drawlater();

delmenu(f.figure_id,gettext('?'));
toolbar(f.figure_id,'on');

gui.user_data = [];
gui.graph_ui= newaxes();
gui.graph_ui.margins = [0.001 0.001 0.001 0.001];
gui.graph_ui.axes_bounds = [0.47,0.03,0.52,0.85];

// Frames creation 
frame_1 = uicontrol("parent",f, "relief","groove", ...
"style","frame", "units","pixels", ...
"position",[ 10, 10, 380, 560], ...
"horizontalalignment","center", "background",[0.9 0.9 0.9], ...
"tag","frame_control");

// positioning
alx = 20; aly = 455; alyd = 20;

uicontrol("parent",f, "style","text",...
"string","$S$", "position",[alx,aly,70,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Total spin of the spin system", ...
"background",[0.9 0.9 0.9]);

gui.S = uicontrol("parent",f, "style","edit",...
"string","0.5", "position",[alx+30,aly,40,20], ...
"horizontalalignment","center", "fontsize",11, ...
"background",[1 1 1], "tag","spin",...
"TooltipString", "Total spin of the spin system", ...
"Callback", 'entry1_callback()');

uicontrol("parent",f, "style","text",...
"string","#", "position",[alx+130,aly,70,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Select spin system", ...
"background",[0.9 0.9 0.9]);

gui.sel_spin = uicontrol("parent",f, "style","edit",...
"string","1", "position",[alx+285,aly,40,20], ...
"horizontalalignment","center", "fontsize",11, ...
"background",[1 1 1], "tag",'sel_spin2',...
"TooltipString", "Select spin system", ...
"Callback","entry_spin_sel_callback()");
gui.sel_spin2 = uicontrol("parent",f, "style","slider",...
"string","1", "position",[alx+150,aly+3,130,15], ...
"horizontalalignment","center", "fontsize",11,'Max',[2],'Min',[1],...
'SliderStep',[1,1],"background",[1 1 1], "tag",'sel_spin2',...
"TooltipString", "Select spin system", ...
"Callback","slider_spin_sel_callback()");

// ordered list of labels
labels1 = ["$g$", "$D$", "$E$", "$U$", "$J\rho_s$", "$\omega_0$",..
 "$T_{0}^2$", "$b$", "$V_{off}$","$\sigma_0$","$T_{eff}$","$\eta_{tip}$",..
  "$B_Z$","$B_Y$","$B_X$","$V_R$"];
// ordered list of default values
values1 = [2, 0, 0, 0, 0, 20, 1, 0, 0, 0, 1, 0, 4, 0, 0, 10];
maxvalues1 = [4, 10, 10, 1, 0.0, 200, 10, 0.05, 5, 1, 10, 1, 20, 20, 20, 200];
minvalues1 = [0, -10, -10, -1, -3, 2, 0, -0.05, -5, -1, 0.1, -1, -20, -20, -20, 2];
checkboxvalues1=[0,0,0,0,0,1,0,1,1,1,0,1,0,0,0,0];
//ordered list of tooltips
ttlabels1 = ["g-factor of the spin",..
"Axial magnetic anisotropy (meV)",..
"In-plane magnetic anisotropy (meV)",..
"Coulomb scattering term",..
"Kondo scattering term",..
"Sample electron bandwidth (meV)",..
"Tip-sample interaction strength",..
"Additional background slope",..
"Additional voltage offset (mV)",..
"Additional background conductance",..
"Effective temperature (K)",..
"Spin polarization in the tip",..
"Magnetic field strength along Z (T)",..
"Magnetic field strength along Y (T)",..
"Magnetic field strength along X (T)",..
"Voltage range (mV)"]

for k=1:size(labels1,2),
     uicontrol("parent",f, "style","text",...
    "string",labels1(k), "position",[alx,aly-k*alyd,28,20], ...
    "horizontalalignment","left", "fontsize",12, ...
    "TooltipString", ttlabels1(k), ...
    "background",[0.9 0.9 0.9]);

    guientry1(k) = uicontrol("parent",f, "style","edit",...
    "string",string(values1(k)), "position",[alx+240,aly-k*alyd,85,20], ...
    "horizontalalignment","center", "fontsize",11, ...
    'Max',1,'Min',0,"TooltipString", ttlabels1(k), ...
    "background",[1 1 1], "tag",labels1(k),"Callback",..
    'entry1_callback()');
    guislider1(k) = uicontrol("parent",f, "style","slider",...
    "string",string(values1(k)), "position",[alx+35,aly-k*alyd+3,200,15], ...
    "horizontalalignment","center", "fontsize",11,'Max',[100],'Min',[0],...
    'SliderStep',[1],"background",[1 1 1], "tag",labels1(k),...
    "TooltipString", ttlabels1(k), ...
    "Callback",'slider1_callback()');
    
    if k<=12 then
        guicheckbox1(k) = uicontrol("parent",f, "style","checkbox",..
        "string","", "position",[alx+335,aly-k*alyd,20,20], ...
        "horizontalalignment","center", "fontsize",11,'Value',checkboxvalues1(k),...
        'SliderStep',[1,10],"background",[0.9 0.9 0.9],..
        "TooltipString", "Disable variable from fitting", ...
        "Callback", 'checkbox1_callback()');
    end
end

uicontrol("parent",f, "style","text",...
"string","# of Spins", "position",[alx,540,150,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Total number of coupled spin systems", ...
"background",[0.9 0.9 0.9]);

gui.nbr_spins = uicontrol("parent",f, "style","edit",...
"string","1", "position",[alx+70,540,40,20], ...
"horizontalalignment","center", "fontsize",11, ...
"background",[1 1 1], "tag","nbr_spins",...
"TooltipString", "Total number of coupled spin systems", ...
"Callback", 'number_spins_callback()');

uicontrol("parent",f, "style","text",...
"string","$\mathcal{C}$", "position",[alx,510,150,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Interaction scaling parameter", ...
"background",[0.9 0.9 0.9]);

gui.sel_heisenberg = uicontrol("parent",f, "style","edit",...
"string","1", "position",[alx+240,510,85,20], ...
"horizontalalignment","center", "fontsize",11, ...
"background",[1 1 1], "tag","sel_heisenberg", ...
"TooltipString", "Interaction scaling parameter", ...
"Callback",'entry1_callback();');

gui.sel_heisenberg2 = uicontrol("parent",f, "style","slider",...
"string","1", "position",[alx+35,510+3,200,15], ...
"horizontalalignment","center", "fontsize",11,'Max',[100],'Min',[0],...
'SliderStep',[1],"background",[1 1 1], "tag",'sel_heisenberg2',...
"TooltipString", "Interaction scaling parameter", ...
"Callback",'slider1_callback()');

uicontrol("parent",f, "style","text",...
"string","$i\infty j$", "position",[alx+20,480,150,20], ...
"TooltipString", "Enable 3rd order scattering also with other spin systems", ...
"horizontalalignment","left", "fontsize",12, ...
"background",[0.9 0.9 0.9]);

guicheckbox1(size(guicheckbox1,1)+1) = uicontrol("parent",f, "style","checkbox",..
"string","", "position",[alx+335,510,20,20], ...
"horizontalalignment","center", "fontsize",11,'Value',1,...
'SliderStep',[1,10],"background",[0.9 0.9 0.9], ..
"TooltipString", "Disable variable from fitting", ...
"Callback",'checkbox1_callback()');

gui.entanglement = uicontrol("parent",f, "style","checkbox",..
"string","", "position",[alx,482,20,20], ...
"horizontalalignment","center", "fontsize",11,'Value',0,...
"background",[0.9 0.9 0.9], ..
"TooltipString", "Enable 3rd order scattering also with other spin systems", ...
 "Callback",'gui_setmode();');
 
gui.mode1 = uicontrol("parent",f, "style","checkbox",..
"string","", "position",[alx+60,482,20,20], ...
"horizontalalignment","center", "fontsize",11,'Value',1,...
"background",[0.9 0.9 0.9], ..
"TooltipString", "Include 3rd order scattering in the calculation", ...
"Callback",'gui_setmode();');

uicontrol("parent",f, "style","text",...
"string","3rd order", "position",[alx+80,480,150,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Include 3rd order scattering in the calculation", ...
"background",[0.9 0.9 0.9]);

gui.mode2 = uicontrol("parent",f, "style","checkbox",..
"string","", "position",[alx+140,482,20,20], ...
"horizontalalignment","center", "fontsize",11,'Value',0,...
"background",[0.9 0.9 0.9], ..
"TooltipString", "Include rate equations in the calculation", ...
"Callback",'gui_setmode();');

uicontrol("parent",f, "style","text",...
"string","Incl. rates", "position",[alx+160,480,150,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Include rate equations in the calculation", ...
"background",[0.9 0.9 0.9]);

// buttonsize and pos
blx = 100; bly = 25; bx=30;by=15;

// Adding button
gui.button_del_all = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx by blx bly], "String","Delete all Graphs", ...
"BackgroundColor",[1,0.6,0.5], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Delete all graphical elements in main Graph", ...
"Callback","gui_del_all()");

gui.button_del = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx by+30 blx bly], "String","Delete last Graph", ...
"BackgroundColor",[1,0.6,0.5], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Delete the last graphical element in main Graph", ...
"Callback","gui_del()");

gui.button_fit = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+120 by blx bly], "String","Fit Data", ...
"BackgroundColor",[0.3,0.9,0.3], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to fit experimental data", ...
"Callback","gui_fit()");

gui.button_draw_spec = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+120 by+30 blx bly], "String","Draw Spectrum", ...
"BackgroundColor",[0.7,0.9,0.7], "fontsize",11, ...
"TooltipString", "Calculate the differential conductance spectrum / spectra", ...
"Relief","raised",...
"Callback","gui_drawspec()");

gui.button_draw_states = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+120 by+60 blx bly], "String","Draw States", ...
"BackgroundColor",[0.7,0.9,0.7], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Calculate the state energies versus magnetic field", ...
"Callback","gui_drawstates()");

gui.button_anisotropy = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+120 by+90 blx bly], "String","Draw Anisotropy", ...
"BackgroundColor",[0.7,0.9,0.7], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Calculate anisotropy energy landscape for the active spin system", ...
"Callback","gui_checkanisotropy();");

gui.button_stopcalc = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx by+90 blx bly], "String","$\blacksquare$", ...
"BackgroundColor",[0.6,0.6,0.9], "fontsize",11, ...
"Relief","raised",...
"foregroundcolor",[0.8 0.8 0.8],...
"enable","off",...
"TooltipString", "Stop the calculation", ...
"Callback","gui_stopcalc(1)");

gui.button_eigenstates = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx by+60 blx bly], "String","Eigenstates", ...
"BackgroundColor",[0.9,0.9,0.5], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to plot further calculated data", ...
"Callback","gui_eigenstates()");

gui.button_switchexp = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+240 by+90 blx bly], "String","$1\Longleftrightarrow 2$", ...
"BackgroundColor",[0.9,0.9,0.5], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Toggle the two experimental parameter sets", ...
"Callback","gui_switchexp();");

gui.button_load = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+240 by+30 blx bly], "String","Load", ...
"BackgroundColor",[0.7,0.7,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Load experimental data or program settings", ...
"Callback","gui_load()");

uicontrol("parent",f, "style","text",...
"string","Row #:", "position",[bx+240,by+55,70,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Number of the column containg the differential conductance data", ...
"background",[0.9 0.9 0.9]);

gui.sel_Load_Row = uicontrol("parent",f, "style","edit",...
"string","3", "position",[bx+300,by+55,40,20], ...
"horizontalalignment","center", "fontsize",11, ...
"TooltipString", "Number of the column containg the differential conductance data", ...
"background",[1 1 1], "tag",'sel_Load_Row');

gui.button_save = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+240 by blx bly], "String","Save", ...
"BackgroundColor",[0.7,0.7,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Save calculated data or program settings", ...
"Callback","gui_save()");

gui.button_tipsample = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+240 535 blx bly], "String","Tip/Sample", ...
"BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to change tip and sample spin polarization", ...
"Callback","gui_tipsample()");

gui.button_couplingmatrix = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+120 535 blx bly], "String","Coupling Matrix", ...
"BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to change interactions beween the spin systems", ...
"Callback","gui_couplingmatrix()");

gui.button_parameters = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+240 480 blx bly], "String","Parameters", ...
"BackgroundColor",[0.7,0.7,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to change global parameters", ...
"Callback","gui_parameters();");

gui.button_limits = uicontrol("parent",f, "style","pushbutton", ...
"Position",[bx+320 140 bly bly], "String","[.,.]", ...
"BackgroundColor",[0.7,0.7,0.9], "fontsize",11, ...
"Relief","raised",...
"TooltipString", "Open submenu to set parameter limits", ...
"Callback","gui_limits();");

gui.allatomsequ = uicontrol("parent",f, "style","checkbox",..
"string","", "position",[alx+80,aly,20,20], ...
"horizontalalignment","center", "fontsize",11,'Value',0,...
"background",[0.9 0.9 0.9], ...
"TooltipString", "Change parameters on all spin systems simultaneously", ...
"Callback",'gui_setmode();');

uicontrol("parent",f, "style","text",...
"string","$\ddagger$", "position",[alx+100,aly,20,20], ...
"horizontalalignment","left", "fontsize",12, ...
"TooltipString", "Change parameters on all spin systems simultaneously", ...
"background",[0.9 0.9 0.9]);

////////////////////////////////////////////////////////////////////////////////
// callback functions
////////////////////////////////////////////////////////////////////////////////

function gui_startcalc(),
    global gui %stopcalc;
    gui.button_stopcalc.enable='on';
    gui.button_stopcalc.foregroundcolor=[1 0.1 0.1];
    %stopcalc=%F;
endfunction
    
function gui_stopcalc(varargin),
    global gui %stopcalc;
    
    [lhs,rhs]=argn(0); 
        gui.button_stopcalc.enable='off';
        %stopcalc=%T;
    if rhs==0 then
        gui.button_stopcalc.foregroundcolor=[0.8 0.8 0.8]; //gray
        cleardata(2); //delete all;
    else
        if varargin(1)=="OK" then
            gui.button_stopcalc.foregroundcolor=[0.8 0.8 0.8]; //gray
           //all o.K
        else,
            gui.button_stopcalc.foregroundcolor=[1 1 0.1]; //yellow
            //interruption
        end;
    end;
    
    //messagebox('calculation will be aborted')
endfunction

function gui_disable()
    global guicheckbox1 guientry1 guislider1;
    
    guicheckbox1(:).enable='off';
    guientry1(:).enable='off';
    guislider1(:).enable='off';
    
endfunction

function gui_enable()
    global guicheckbox1 guientry1 guislider1 gui experiment;
    guientry1(:).enable='on';
    guislider1(13:16).enable='on';
    guicheckbox1(:).enable='on';
    checkbox1_callback()
endfunction


function cleardata(a)
    
    global gui experiment calc;
    calc.spec=[];
    if a>=1 then
        calc.spec_raw=[];
        calc.occ=[];
        calc.lifetime=[];
        calc.entropy=[];
    end
    if a>=2 then
        experiment.Eigenval=[];
        experiment.Eigenvec=[];
        calc.states=[];
        calc.giantspin=[];
        calc.negativity=[];
    end

endfunction

function checkbox1_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;

    if evstr(gui.S.String)==0.5 then
        guicheckbox1(2).Value=1; //swich off D and E for S=0.5
        guicheckbox1(3).Value=1;
    end
    
    if experiment.paramagnetic then
       guicheckbox1(12).Value=1; //swich off rho_tip for a paramagnetic tip
    end
    
    for i= 1:size(guicheckbox1,1)-1     //last entry is Heisenberg Coupling. Treat seperately.
        if guicheckbox1(i).Value==0 then
            guientry1(i).enable="on";
            guislider1(i).enable="on";
            experiment.sw(i)=%T;
        else
            guientry1(i).enable="off";
            guislider1(i).enable="off";
            experiment.sw(i)=%F;
        end
    end
       
    i=size(guicheckbox1,1);   //Heisenberg Coupling
    
    if guicheckbox1(i).Value==0 & size(experiment.atom,2)>1 then
        gui.sel_heisenberg.enable="on";
        gui.sel_heisenberg2.enable="on";
         experiment.sw(i)=%T;
    else
        gui.sel_heisenberg.enable="off";
        gui.sel_heisenberg2.enable="off";
        guicheckbox1(i).Value=1;
         experiment.sw(i)=%F;
    end
    

endfunction

function slider1_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    
    for i= 1: size(guislider1,1)
         temp=guislider1(i).Value;
         maxi=maxvalues1(i);
         mini=minvalues1(i);
         r=maxi-mini;
         guientry1(i).string=string(mini+r/100*temp);
    end

    // Heisenberg slider
    temp=gui.sel_heisenberg2.Value;
    gui.sel_heisenberg.string=string(-10+20/100*temp);
    
    update_atomlink();
    
endfunction

function entry1_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    
    for i= 1: size(guislider1,1)
         guientry1(i).string(~isnum(guientry1(i).string))='0'; //replace bullshit
    end
    
    // Spin entry
    gui.S.string(~isnum(gui.S.string))='0'; //replace bullshit
    temp=round(evstr(gui.S.string)*2);
    if temp<1 then
        temp=1;
    elseif temp>20 then
        temp=20;
    end
    gui.S.String=string(temp/2);
    if temp==1 then checkbox1_callback(); end;
    
    // Heisenberg entry
    gui.sel_heisenberg.String(~isnum(gui.sel_heisenberg.String))='0'; //replace bullshit
        
    update_slider();
    update_atomlink();
    
endfunction

function update_slider(),
    
    global guientry1 guislider1 gui;
    
    for i= 1: size(guislider1,1)
         temp=evstr(guientry1(i).string);
         maxi=maxvalues1(i);
         mini=minvalues1(i);
         r=maxi-mini;
        guislider1(i).Value=(temp-mini)*100/r;
    end

    // Heisenberg entry
    temp=evstr(gui.sel_heisenberg.String);
    gui.sel_heisenberg2.Value=(temp+10)*100/20;
    
endfunction

function slider_spin_sel_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    gui.sel_spin2.Value=round(gui.sel_spin2.Value);
    gui.sel_spin.String=string(gui.sel_spin2.Value);
    if experiment.rate_calc then
        cleardata(1); //spectral data is now invalid
    end
    update_gui_values();

endfunction

function entry_spin_sel_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    gui.sel_spin.String(~isnum(gui.sel_spin.String))='1'; //replace bullshit
    temp=round(evstr(gui.sel_spin.String))
    if temp<1 then 
        temp=1;
    elseif temp>evstr(gui.nbr_spins.String) then
        temp=evstr(gui.nbr_spins.String);
    end;
    gui.sel_spin.String=string(temp);
    gui.sel_spin2.Value=temp;
    
    update_gui_values();
    
endfunction

function number_spins_callback(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    
    gui.nbr_spins.String(~isnum(gui.nbr_spins.String))='0'; //replace bullshit
    temp=round(evstr(gui.nbr_spins.String));
    if temp>12 then 
        temp=12;
    end
    if temp<=1 then 
        temp=1;
        gui.sel_spin.Enable="off";
        gui.sel_spin2.Enable="off";
        gui.sel_heisenberg.Enable="off";
        gui.sel_heisenberg2.Enable="off";
        guicheckbox1(size(guicheckbox1,1)).Value=1;    //the last entry is the Heiseberg coupling
        gui.button_couplingmatrix.Enable="off";
        if gui.mode2.Value==1 then
            gui.button_fit.Enable="off";
        else
            gui.button_fit.Enable="on";
        end
        gui.sel_spin2.Value=1;
        gui.sel_spin.String="1";
        gui.entanglement.Visible="off";
        gui.allatomsequ.Visible="off";
    else
        gui.sel_spin.Enable="on";
        gui.sel_spin2.Enable="on";
        gui.sel_heisenberg.Enable="on";
        gui.sel_heisenberg2.Enable="on";
        guicheckbox1(size(guicheckbox1,1)).Value=0;    //the last entry is the Heiseberg coupling
        if temp > 2 | gui.mode2.Value==1 then
            gui.button_fit.Enable="off";
        else
            gui.button_fit.Enable="on";
        end
        gui.entanglement.Visible="on";
        gui.button_couplingmatrix.Enable="on";
        gui.allatomsequ.Visible="on";
        if size(experiment.matrix,1) <> (temp-1) then
            experiment.matrix=resize_matrix(experiment.matrix,temp-1,temp-1);
            experiment.matrix(find(experiment.matrix==''))='0';
        end;
        if size(experiment.matrixDM,1) <> (temp-1) then
            experiment.matrixDM=resize_matrix(experiment.matrixDM,temp-1,temp-1);
            experiment.matrixDM(find(experiment.matrixDM==''))='0, 0, 0';
        end;
    end;
    if  gui.sel_spin2.Value > temp then
        gui.sel_spin2.Value=temp;
        gui.sel_spin.String=string(temp);
        update_gui_values();
    end
    
    gui.nbr_spins.String=string(temp);
    gui.sel_spin2.Max=temp;
    gui.sel_spin2.Value=evstr(gui.sel_spin.String);
    update_atomlink(); 
    
endfunction

function update_atomlink(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment gh;
    
    gui.nbr_spins.String(~isnum(gui.nbr_spins.String))='1'; //replace bullshit
    number_atoms=evstr(gui.nbr_spins.String);
    atomlink=experiment.atom;
    size_atomlink=size(atomlink,2);
    
    if size_atomlink < number_atoms then
        for i=size_atomlink+1:number_atoms,
            atomlink=[atomlink,atomlink(i-1)];   
        end;
        cleardata(2); //all data is now invalid
    elseif size_atomlink > number_atoms then    
        al=atomlink(1);
        for i=2:number_atoms,
            al=[al,atomlink(i)];
        end,
        atomlink=al;
        cleardata(2); //all data is now invalid
    end;
   
    number=gui.sel_spin2.Value;
    atomlinkold=atomlink(number);
    
    if gui.allatomsequ.Value==1 & number_atoms >= 2 then
        
        atomlink(:).S=evstr(gui.S.String);
        atomlink(:).g=evstr(guientry1(1).String);
        atomlink(:).D=evstr(guientry1(2).String);
        atomlink(:).E=evstr(guientry1(3).String);

        if or(atomlinkold<>atomlink(number)) then
            cleardata(2); //all data is now invalid
        end
        
        atomlink(:).U=evstr(guientry1(4).String);
        atomlink(:).J=evstr(guientry1(5).String);
        atomlink(:).w=evstr(guientry1(6).String);

        if or(atomlinkold<>atomlink(number)) then
            cleardata(1); //spectral data is now invalid
        end;
    
    else
    
        atomlink(number).S=evstr(gui.S.String);
        atomlink(number).g=evstr(guientry1(1).String);
        atomlink(number).D=evstr(guientry1(2).String);
        atomlink(number).E=evstr(guientry1(3).String);

        if or(atomlinkold<>atomlink(number)) then
            cleardata(2); //all data is now invalid
        end

        atomlink(number).U=evstr(guientry1(4).String);
        atomlink(number).J=evstr(guientry1(5).String);
        atomlink(number).w=evstr(guientry1(6).String);
        
        if or(atomlinkold<>atomlink(number)) then
            cleardata(1); //spectral data is now invalid
        end
    end

    experiment.atom=atomlink;    //play it back to experiment
    
    old=experiment.heisenberg_coupling;
    experiment.heisenberg_coupling=evstr(gui.sel_heisenberg.string);    
    if old<>experiment.heisenberg_coupling then
        cleardata(2); //all data is now invalid
    end
    
    old=experiment.B;
    experiment.B=...
    [evstr(guientry1(15).String),evstr(guientry1(14).String),evstr(guientry1(13).String)];
    if or(old<>experiment.B) then
        cleardata(2); //all data is now invalid
    end
    
    old=experiment.ptip;    
    if experiment.paramagnetic then
        //calculate the splitting energy
        delta=sqrt(sum(experiment.B.^2))*0.0588*experiment.paramag_g*experiment.paramag_S;
        if delta<>0 then
            S.S=experiment.paramag_S;
            polarization=AvrgM(S,delta,experiment.T)*experiment.eta;
            experiment.ptip=polarization*experiment.B/sqrt(sum(experiment.B.^2));
            // update gui
            guientry1(12).String=string(polarization);
            update_slider();
        else
            experiment.ptip=[0 0 0];
            // update gui
            guientry1(12).String='0';
            guislider1(12).Value=50;
        end;
    else
        if sum(experiment.B.^2)<>0 then
        
            if sum(experiment.ptip.^2)<>0 then
                //calculate angle between B and ptip
                angle=real(acos((experiment.ptip*experiment.B')...
                /(sqrt(sum(experiment.ptip.^2))*sqrt(sum(experiment.B.^2)))));
                sig=1-2*(angle>%pi/2); //if angle>pi/2 then sig is -1, else +1;
            
                experiment.ptip=experiment.ptip/sqrt(sum(experiment.ptip.^2))*...
                evstr(guientry1(12).string)*sig;
        
            else
                //allign in direction of B
                experiment.ptip=experiment.B/sqrt(sum(experiment.B.^2))*...
                evstr(guientry1(12).string);
            end
        else
            experiment.ptip=[0 0 0];
        end
    end
    if or(old<>experiment.ptip) then
        cleardata(1);
    end
    
    old=experiment.A;
    experiment.A=evstr(guientry1(7).String);
    if old<>experiment.A then
        if experiment.rate_calc then 
            cleardata(1); //spectral data is now invalid 
        else
            cleardata(0); //only delete spec.calc
        end;
    end
    old=experiment.b;
    experiment.b=evstr(guientry1(8).String);
    if old<>experiment.b then cleardata(0); //only delete spec.calc
    end
    old=experiment.x0;
    experiment.x0=evstr(guientry1(9).String);
    if old<>experiment.x0 then cleardata(0); //only delete spec.calc
    end
    old=experiment.y0;
    experiment.y0=evstr(guientry1(10).String);
    if old<>experiment.y0 then cleardata(0); //only delete spec.calc
    end
    old=experiment.xrange;
    experiment.xrange=evstr(guientry1(16).String);
    if experiment.xrange<=0 then 
        experiment.xrange=old;  //xrange >0!
        guientry1(16).String=string(old);
    end
    if old<>experiment.xrange then cleardata(1); //spectral data is now invalid 
    end
    old=experiment.T;
    experiment.T=0.08617*evstr(guientry1(11).String);
    //the factor corresponds to 1K=0.08617meV, i.e. is k_B/e
    if old<>experiment.T then cleardata(1); //spectral data is now invalid 
    end
    
    ierr = execstr("delete(g.children)", "errcatch"); //figure out of figure g exisit
    if ~ierr then
        plt_dmatrix();                                //yes then update figure
    end
    
    ierr = execstr("delete(gh.children)", "errcatch"); //figure out of figure gh exisit
    if ~ierr then
       gui_checkanisotropy();                                //yes then update figure
    end
    
    
    //check that 3*|E|<=|D|. If not make the star "red"
    if 3*abs(atomlink(number).E)>abs(atomlink(number).D) | atomlink(number).E<0 then
        gui.button_anisotropy.foregroundcolor=[1 0.2 0.2]
    else
        gui.button_anisotropy.foregroundcolor=[0 0 0];
    end
    
endfunction
    
function update_gui_values(),
    
    global guicheckbox1 guientry1 guislider1 gui experiment;
    
    atomlink=experiment.atom;
    gui.nbr_spins.String=string(size(atomlink,2));
    gui.sel_heisenberg.String=string(experiment.heisenberg_coupling);
    
    gui.entanglement.value=1*(experiment.entanglement);
    gui.mode1.value=1*(experiment.third_order_calc);
    gui.mode2.value=1*(experiment.rate_calc);
    
    number=gui.sel_spin2.Value;
    
    gui.S.String=string(atomlink(number).S);
    guientry1(1).String=string(atomlink(number).g);
    guientry1(2).String=string(atomlink(number).D);
    guientry1(3).String=string(atomlink(number).E);
    guientry1(4).String=string(atomlink(number).U);
    guientry1(5).String=string(atomlink(number).J);
    guientry1(6).String=string(atomlink(number).w);
    guientry1(7).String=string(experiment.A);
    guientry1(8).String=string(experiment.b);
    guientry1(9).String=string(experiment.x0);
    guientry1(10).String=string(experiment.y0);
    guientry1(11).String=string(experiment.T/0.08617);
    //the factor corresponds to 1K=0.08617meV, i.e. is k_B/e
    guientry1(16).String=string(max(experiment.xrange));
    
    //calculate angle between B and ptip
    angle=real(acos((experiment.ptip*experiment.B')/...
    (sqrt(sum(experiment.ptip.^2))*sqrt(sum(experiment.B.^2)))));
    //if angle is larger than 90 deg eta<0
    //eta is the length of experiment.ptip
    if angle>%pi/2 then
        guientry1(12).String=string(-sqrt(sum(experiment.ptip.^2)));
    else
        guientry1(12).String=string(sqrt(sum(experiment.ptip.^2)));
    end
    guientry1(15).String=string(experiment.B(1));
    guientry1(14).String=string(experiment.B(2));
    guientry1(13).String=string(experiment.B(3));
    
    update_slider();gui_setmode();
    
endfunction


function gui_setmode(),
    
    global gui experiment;
    
    oldval=experiment.entanglement;
    if gui.entanglement.Value==1 then
        experiment.entanglement=%T;
    else
        experiment.entanglement=%F;
    end;
    if oldval<>experiment.entanglement then
        cleardata(1); //spectral data is now invalid 
    end
    
    oldval=experiment.rate_calc;
    if gui.mode2.Value==1 then
        experiment.rate_calc=%T;
    else
        experiment.rate_calc=%F;
    end;
    if oldval<>experiment.rate_calc then
        cleardata(1); //spectral data is now invalid 
    end
    
    oldval=experiment.third_order_calc;
    if gui.mode1.Value==1 then
        experiment.third_order_calc=%T;
    else
        experiment.third_order_calc=%F;
    end;
    if oldval<>experiment.third_order_calc then
        cleardata(1); //spectral data is now invalid 
    end
    
    if gui.mode2.Value==1 then
       gui.button_fit.Enable="off";
    elseif round(evstr(gui.nbr_spins.String))<=2 then
       gui.button_fit.Enable="on";
    end;

endfunction

function gui_tipsample(),
    
   global experiment gui gg g;
   
   ierr = execstr("close(g)", "errcatch");
   g=figure('figure_position',[1000,0],'figure_size',[500,600],'auto_resize',..
   'on','figure_name',..
   '3rd order tunneling simulator. (c) Markus Ternes ');
   gg.data=[];

   plt_dmatrix();
    
endfunction
       
function plt_dmatrix(),
    
   global experiment guicheckbox1 guientry1 guislider1 gui g gg;
   
   drawlater();
   scf(g);
   subplot(121);
   mat=dmatrix(experiment.ptip);
   mat=round(mat*1000)/1000;
   strmat=strsubst(string(mat), '%i*', 'i\times ');
   str=+"$\\ \mbox{Density matrix:}\\ \begin{pmatrix}"+strmat(1,1)+..
   "&"+strmat(2,1)+"\\"+...
   strmat(2,1)+"&"+strmat(2,2)+"\end{pmatrix}$";
   xtitle(str);
   blochsphere(mat,'red');
   subplot(122);
   mat=dmatrix(experiment.psample);
   mat=round(mat*1000)/1000;
   strmat=strsubst(string(mat), '%i*', 'i\times ');
   str=+"$\\ \mbox{Density matrix:}\\ \begin{pmatrix}"+strmat(1,1)+..
   "&"+strmat(2,1)+"\\"+...
   strmat(2,1)+"&"+strmat(2,2)+"\end{pmatrix}$";
   xtitle(str);
   blochsphere(mat,'blue');
   drawnow();
    
   uicontrol("parent",g, "relief","groove", ...
   "style","frame", "units","pixels", ...
   "position",[10, 5, 480, 70], ...
   "horizontalalignment","center", "background",[0.9 0.9 0.9], ...
   "tag","frame_control");

   gg.button_change = uicontrol("parent",g, "style","pushbutton", ...
   "Position",[200 40 100 25], "String","Change", ...
   "BackgroundColor",[0.6,0.9,0.9], "fontsize",12, ...
   "Relief","raised",...
   "TooltipString", "Change spin polarization in tip and sample",..
   "Callback","gui2_change();");

   gg.button_ok = uicontrol("parent",g, "style","pushbutton", ...
   "Position",[200 10 100 25], "String","OK", ...
   "BackgroundColor",[0.6,0.9,0.6], "fontsize",12, ...
   "Relief","raised",...
   "TooltipString", "Close submenu",..
   "Callback","close(g)");

   uicontrol("parent",g, "style","text",...
   "string","Tip", "position",[60,80,140,30], ...
   "horizontalalignment","center", "fontsize",18, ...
   "background",[0.9 0.9 0.9]);

   uicontrol("parent",g, "style","text",...
   "string","Sample", "position",[300,80,140,30], ...
   "horizontalalignment","center", "fontsize",18, ...
   "background",[0.9 0.9 0.9]);

   uicontrol("parent",g, "style","checkbox",..
   "string","Paramag.", "position",[70,10,110,25], ...
   "horizontalalignment","center", "fontsize",12,'Value',..
   1*experiment.paramagnetic,"background",[0.9 0.9 0.9],..
    "TooltipString", "Paramagnetic tip. Polarization will be calculated",..
    "Callback","experiment.paramagnetic=~experiment.paramagnetic;ts_para_callback();");

//    uicontrol("parent",g, "style","checkbox",..
//   "string","Entangle Sample", "position",[320,10,140,25], ...
//   "horizontalalignment","center", "fontsize",12,'Value',..
//   1*experiment.sample_entanglement,"background",[0.9 0.9 0.9],..
//    "Callback",...
//    "experiment.sample_entanglement=~experiment.sample_entanglement;...
//    cleardata(1);ts_para_callback()");

    uicontrol("parent",g, "style","text",...
    "string","$g$", "position",[25,35,140,25], ...
    "horizontalalignment","left", "fontsize",12, ...
    "TooltipString", "g-factor of the tip",..
    "background",[0.9 0.9 0.9]);

    gg.gui_paramag_g=uicontrol("parent",g, "style","edit",...
    "string",string(experiment.paramag_g), "position",[40,40,40,20], ...
    "horizontalalignment","center", "fontsize",12, ...
    "background",[1 1 1], "tag","para_g",..
    "Enable",1*experiment.paramagnetic,..
    "TooltipString", "g-factor of the tip",..
    "Callback",'ts_para_callback()');

    uicontrol("parent",g, "style","text",...
    "string","$S$", "position",[25,10,40,25], ...
    "horizontalalignment","left", "fontsize",12, ...
    "TooltipString", "Total spin of tip",..
    "background",[0.9 0.9 0.9]);

    gg.gui_paramag_S=uicontrol("parent",g, "style","edit",...
    "string",string(experiment.paramag_S), "position",[40,15,40,20], ...
    "horizontalalignment","center", "fontsize",12, ...
    "background",[1 1 1], "tag","para_g",..
    "Enable",1*experiment.paramagnetic,..
    "TooltipString", "Total spin of tip",..
    "Callback",'ts_para_callback()');

    uicontrol("parent",g, "style","text",...
    "string","$\eta_{max}$", "position",[105,35,40,25], ...
    "horizontalalignment","left", "fontsize",12, ...
    "TooltipString", "Maximal spin polarization of tip",..
    "background",[0.9 0.9 0.9]);
    
    gg.gui_eta=uicontrol("parent",g,"style","edit",...
    "string",string(experiment.eta), "position",[140,40,40,20], ...
    "horizontalalignment","center", "fontsize",12, ...
    "background",[1 1 1], "tag","para_eta",..
    "Enable",1*experiment.paramagnetic,..
    "TooltipString", "Maximal spin polarization of tip",..
    "Callback",'ts_para_callback()');

//    uicontrol("parent",g, "style","text",...
//    "string","$J\rho_0\times$", "position",[320,35,40,25], ...
//    "horizontalalignment","left", "fontsize",12, ...
//    "background",[0.9 0.9 0.9]);

//    gg.gui_sef=uicontrol("parent",g,"style","edit",...
//    "string",string(experiment.sef), "position",[360,40,40,20], ...
//    "horizontalalignment","center", "fontsize",12, ...
//    "background",[1 1 1], "tag","sef","Callback",...
//    'ts_para_callback()');
    
endfunction

function gui2_change(),
   
   global experiment guicheckbox1 guientry1 guislider1 gui g;

   labelh=["Tip","Sample"];
   labelv=["x","y","z"];
   str=string([experiment.ptip;experiment.psample])';
   new=x_mdialog("Spin Polarisation",...
   labelv,labelh,str);
   if size(new)==[3,2] then
       new(~isnum(new))='0'; //replace bullshit and set it to '0'  
       if or(new<>str) then
          experiment.ptip=evstr(new(:,1))';
          experiment.psample=evstr(new(:,2))';
          cleardata(1);
       end
   end
   amp=sqrt(sum(experiment.ptip.^2));
   if amp>1 then
       experiment.ptip=experiment.ptip/amp;
   end
   amp=sqrt(sum(experiment.psample.^2));
   if amp>1 then
       experiment.psample=experiment.psample/amp;
   end
   ts_para_callback();
   
endfunction

function ts_para_callback(),
    
    global experiment gg g guicheckbox1 guientry1 guislider1 gui;

    str=gg.gui_eta.String;
    str(~isnum(str))='0'; //replace bullshit and set it to '0'
    if experiment.eta<>evstr(str) then
        experiment.eta=evstr(str);
        cleardata(1);
    end
    str=gg.gui_paramag_g.String;
    str(~isnum(str))='2'; //replace bullshit and set it to '2'
    if experiment.paramag_g<>evstr(str) then
        experiment.paramag_g=evstr(str);
        cleardata(1);
    end
    
    str=gg.gui_paramag_S.String;
    str(~isnum(str))='0.5'; //replace bullshit and set it to '0.5'
    if experiment.paramag_S<>evstr(str) then
        experiment.paramag_S=evstr(str);
        cleardata(1);
    end

//    str=gg.gui_sef.String;
//    str(~isnum(str))='1'; //replace bullshit and set it to '1'
//    if experiment.sef<>evstr(str) then
//        experiment.sef=evstr(str);
//        cleardata(1);
//    end
//
    update_gui_values();
    update_atomlink();
    
endfunction

function gui_couplingmatrix(),
    
   global experiment ok h hh;

   nbr=size(experiment.atom,2); //number of spins
   
   ierr = execstr("close(h)", "errcatch");
  
   h=figure('figure_position',[1000,0],'figure_size',[500,500],'auto_resize',..
   'on','figure_name',..
   '3rd order tunneling simulator. (c) Markus Ternes ');
   hh.data=[];
   hh.graph_ui=newaxes();
   hh.graph_ui.margins = [ 0 0 0 0];
   hh.graph_ui.axes_bounds = [0.1,0.1,0.8,0.8];
   plot2d(0,0,-1,"010"," ",[-1.5,-1.5,1.5,1.5]);
   H_sw=0;
   
   hh.button_change1 = uicontrol("parent",h, "style","pushbutton", ...
   "Position",[200 10 80 25], "String","Heisenberg", ...
   "BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
   "Relief","raised",...
   "TooltipString", "Change Heisenberg coupling constants. Use one value of isotropic, otherwise three values",..
   "Callback","change_coupling(1)");
   
//   hh.button_sw1 = uicontrol("parent",h, "style","checkbox",..
//   "position",[280,10,20,20], ...
//   "horizontalalignment","center", "fontsize",11,'Value',H_sw,...
//   "background",[0.9 0.9 0.9], "Callback",'change_coupling(1)');

   hh.button_change2 = uicontrol("parent",h, "style","pushbutton", ...
   "Position",[60 10 80 25], "String","DM", ...
   "BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
   "Relief","raised",...
   "TooltipString", "Change antisymmetric exchange constants",..
   "Callback","change_coupling(2)");

//   hh.button_sw2 = uicontrol("parent",h, "style","checkbox",..
//   "position",[140,10,20,20], ...
//   "horizontalalignment","center", "fontsize",11,'Value',H_sw,...
//   "background",[0.9 0.9 0.9], "Callback",'change_coupling(2)');

   hh.button_ok = uicontrol("parent",h, "style","pushbutton", ...
   "Position",[340 10 100 25], "String","OK", ...
   "BackgroundColor",[0.6,0.9,0.6], "fontsize",11, ...
   "Relief","raised",...
   "TooltipString", "Close submenu",..
   "Callback","close(h)");
   
   plt_coupling();

endfunction

function plt_coupling(),
   
   global experiment h hh;

   mH=experiment.matrix;
   mDM=experiment.matrixDM;
   atomlink=experiment.atom;
   nbr=size(atomlink,2); //number of spins
   scf(h);
   if hh.graph_ui.children<>[] then
       delete(hh.graph_ui.children);
   end;
   xv=[];yv=[];z=[];
   for i=1:size(mH,1),
      for j=1:size(mH,2),
         xvv=[sin(2*%pi/nbr*(i-1));sin(2*%pi/nbr*j)];
         yvv=[cos(2*%pi/nbr*(i-1));cos(2*%pi/nbr*j)];
         if sum(evstr(mH(i,j)).^2)<>0 then,
            xv=[xv,xvv];
            yv=[yv,yvv];
            if sum(evstr(mH(i,j)))>0 then,
               z=[z,1];
            else
               z=[z,5];
            end;
         end;
         if sum(evstr(mDM(i,j)).^2)<>0 then,
             x=[];y=[];
             for k=0:0.01:1,
                dy=yvv(1)-yvv(2);
                dx=xvv(1)-xvv(2);
                l=sqrt(dx^2+dy^2);
                x=[x;xvv(2)+k*dx+0.03*sin(k*8*%pi*l)*dy/l];
                y=[y;yvv(2)+k*dy-0.03*sin(k*8*%pi*l)*dx/l];  
             end;
             plot2d(x,y,2,'000');
         end;
      end;
   end;
   
   xsegs(xv,yv,z);
  
   for i=0:nbr-1,
     xset("color",atomlink.S(i+1)*2)
     xfarc(sin(2*%pi/nbr*i)-0.1,cos(2*%pi/nbr*i)+0.1,0.2,0.2,0,360*64);
     xstring(1.2*sin(2*%pi/nbr*i)-0.1,1.2*cos(2*%pi/nbr*i)-0.1,"#:"+string(i+1)) 
   end
   
endfunction

function change_coupling(a),
      
   global experiment hh;
   nbr=size(experiment.atom,2); //number of spins
   row="Spin: ";labelv=row(ones(1,nbr-1))+string(1:nbr-1);
   col="Spin: ";labelh=col(ones(1,nbr-1))+string(2:nbr);
   if a==1 then
       str=experiment.matrix;
       diagtxt="Heisenberg coupling between two spins";
   else
       str=experiment.matrixDM;
       diagtxt="Dzyaloshinsky-Moriya coupling between two spins";
   end
   
   for i=1:size(str,2)-1,
       str(i+1:$,i)="do not edit";
   end;
   new=x_mdialog(diagtxt,...
   labelv,labelh,str);
   if size(new)==size(str) then
       if or(new<>str) then
           if a==1 then
               new(find(new=='do not edit'))='0';
               experiment.matrix=new;
               cleardata(2);
           else
               new(find(new=='do not edit'))='0, 0, 0';
               experiment.matrixDM=new;
               cleardata(2);
           end;
       end;
   end;
   plt_coupling();
       
endfunction

function gui_drawspec(),
    
  global f guientry1 guislider1 gui experiment calc;
    
  if experiment.Eigenval==[] then
      eigenvalues(experiment);
  end;
  
  scf(f);
  nbr_of_atoms=size(experiment.atom,2);
  nbr_of_states=size(experiment.Eigenvec,2);
  maxcnt=nbr_of_states*nbr_of_atoms; 
 
  
  if ~experiment.rate_calc & calc.spec_raw==[] then //no rate calculation
      
    cnt=0;
    winH=waitbar('Calculating Spectrum');
    
    daty=[];
    occ=Occupation(experiment.Eigenval,experiment.T);
    
    for atnr=1:nbr_of_atoms,
        experiment.position=atnr;
        experiment.jposition=experiment.position
        // second order calculation
        [x,y]=spec2(experiment);
        if %savedata then
            csvWrite([x real(y)],"data_2nd"+string(atnr)+".dat"," "); 
        end;
    
        // third order calculation
        y2=[];
        gui_startcalc();
        if experiment.third_order_calc then
            for i=1:size(experiment.Eigenvec,2),
                if occ(i) > %precission then
                    if ~%stopcalc then
                         waitbar(cnt/maxcnt,['Calculating Spectrum';..
                        ' ';'Evaluate State '+string(i)+..
                        ' with tip at atom '+string(atnr)],winH);
                    else
                        close(winH);
                        gui_stopcalc();
                        return;
                    end
                    [x,y1,y1r]=spec3(experiment,i);
                    //sc=experiment.atom(experiment.jposition).S;
                    
                    y2=y2+(y1+y1r); 
                end,
                cnt=cnt+1;
            end;
            if %savedata then
                    csvWrite([x real(y2)],"data_inelastic"+string(atnr)+..
                    ".dat"," "); 

            end;
        end;
        scf(f);
        daty=[daty,y+y2];
        //daty=[daty,(y+y2+experiment.y0+experiment.b*x)*scale];
        if %savedata then
            csvWrite([x real(y+y2)],"data_inelastic_all"+string(atnr)+".dat"," ");
        end;
    end;
    gui_stopcalc("OK");
    close(winH);
    calc.spec_raw=[x,daty];
    //calc.spec=[x+experiment.x0,daty];  
    
   
  elseif experiment.rate_calc & ( calc.spec_raw==[] | experiment.position<>gui.sel_spin2.value ) then  
    //rate calculation
   
    J2_ts=experiment.A;
       
    ve=real(experiment.Eigenval);
    if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
        ve=diag(ve);
    end;
    ve=ve-min(real(ve));
    if size(ve,1)==1 then      //change ve to column vector if ve is row vector
        ve=ve'; 
    end;
    //calculate delta_E between the states
    ediff=ones(1:size(ve,1))'.*.ve'-ones(1:size(ve,1)).*.ve;

    //initialize output variables
    y=zeros(1000,nbr_of_states);I=zeros(1000,1);ltime=zeros(1000,nbr_of_states);

    experiment.position=gui.sel_spin2.value;
    experiment.jposition=gui.sel_spin2.value;
    
    rate_ts=Rate2nd2(experiment)';
    
    rate_st=rate_ts';

    tempexperiment=experiment;
    tempexperiment.ptip=experiment.psample;
    tempexperiment.atom(:).U=0;
    
    rate_ss=tempexperiment.atom(experiment.position).J^2*Rate2nd2(tempexperiment)'; 
    
    //rate_ss=[];
    //for atnr=1:nbr_of_atoms,
    //    tempexperiment.position=atnr;
    //    rate_ss=rate_ss+tempexperiment.atom(atnr).J^2*Rate2nd2(tempexperiment)'; 
    //end
    
    // in principle we should do the summation over all atoms, but this will 
    // lead to unavoidable problems (missing deconstruction of entanglements)
    // which can not be handled in this model. 
    // ("two weakly coupled spins problem")
    // I would need a more complex treatment via Bloch-Redifeld
    
    rate2_ss=(fbox((ediff)/experiment.T)*experiment.T).*rate_ss;
    
    gui_startcalc();
    
    if experiment.third_order_calc then
        
        experiment.jposition=experiment.position;
        [rate3_st,rate3_ts]=spec3rate(experiment);
        rate3_ts=-rate3_ts;
        rate3_ss=spec3rate_ss(experiment)*experiment.atom(experiment.position).J^2;
        
        rate3_ts=rate3_ts*J2_ts;
        rate3_st=-rate3_st*J2_ts;
    end;
    
    if %stopcalc then
        gui_stopcalc();
        return;
    end
    i=0;
    x=linspace(experiment.xrange,-experiment.xrange,1000);
    
    winH=waitbar('Calculating Spectrum (searching the matrix kernel)');
    for U=x,
        i=i+1;
        rate2_ts=J2_ts*fbox((ediff+U)/experiment.T)*experiment.T.*rate_ts;
        rate2_st=J2_ts*fbox((ediff-U)/experiment.T)*experiment.T.*rate_st;
        
        if experiment.third_order_calc then    
            rate2=rate2_ss+rate3_ss+rate2_ts+rate2_st+rate3_ts(:,:,i)+...
            rate3_st(:,:,i);
        else
            rate2=rate2_ss+rate2_ts+rate2_st;
        end;
        
        rate21=rate2-eye(rate2).*rate2-diag(sum(rate2-eye(rate2).*rate2,1));
        [ststsol]=kernel(rate21); //find steady-state solution
        sc=sum(ststsol,1);
        stst=ststsol(:,1)/sc(1);  //normalize to get occupancy of the states
        
        y(i,:)=stst';
        
        //the inverse of the lifetime is:
        ltime(i,:)=sum(rate21-rate21.*eye(rate21),1);
        
        if  experiment.third_order_calc then
            I(i)=sum(rate2_ts*stst)-sum(rate2_st*stst)+...
            sum(rate3_ts(:,:,i)*stst)-sum(rate3_st(:,:,i)*stst);
        else
            I(i)=sum(rate2_ts*stst)-sum(rate2_st*stst);    
        end;
        if ~%stopcalc then
            waitbar(i/1000,'Calculating Spectrum (searching the matrix kernel)',winH);
        else
            close(winH);
            gui_stopcalc();
            return;
        end

    end; 

    gui_stopcalc("OK");
    close(winH);
    
    // calculate dI/dV
    di=-(I(2:$)-I(1:$-1))*500/experiment.xrange;
    
    xx=x-experiment.xrange/999;
    xx=xx(1:$-1);
        
    di=di/experiment.A;
    
    calc.spec_raw=[xx',di];
    calc.occ=[x',y];
    calc.lifetime=[x',ltime.^-1*6.582e-13*2]; //
     
  end;    
//daty=[daty,(y+y2+experiment.y0+experiment.b*x)*scale];
  if calc.spec==[] then
      if ~experiment.rate_calc then
          if %normalize then 
            atnr=experiment.position;
            scale=2*(experiment.atom(atnr).S*(experiment.atom(atnr).S+1)+experiment.atom(atnr).U^2)^-1;
          else 
            scale=experiment.A;
          end;
      else
          if %normalize then 
            scale=1;
          else 
            scale=experiment.A;
          end;
      end;
      calc.spec=[calc.spec_raw(:,1)+experiment.x0];
      for i=2:size(calc.spec_raw,2),
          calc.spec=[calc.spec,(calc.spec_raw(:,i)+experiment.y0+experiment.b*calc.spec_raw(:,1))*scale];
      end
  end;
  scf(f);
  plot2d(calc.spec(:,1),calc.spec(:,2:$));

  if ~experiment.rate_calc then
     str='Spin #:'+string(1:nbr_of_atoms); 
     ylabeltext="dI/dV (a.u.)";
  else
     str='Spin #:'+string(experiment.position);
     ylabeltext="dI/dV (quantum of conductance)";
  end
  
  //captions(gui.graph_ui.children.children($),str);
  captions(gui.graph_ui.children(1).children,str);
  gui.graph_ui.x_label.text="eV (mV)";
  gui.graph_ui.y_label.text=ylabeltext;

endfunction

function gui_drawstates(),
    
    global f gui experiment calc;
    
    if sum(experiment.B.^2)==0 then
        messagebox("B-field is zero!");
        abort;
    end
    
    plotdrawn=0;
    if calc.states==[] then
        //calculate the number of eigenstates
        nbr=1;
        atomlink=experiment.atom;
        for i=1:size(atomlink,2),
            nbr=nbr*(2*atomlink.S(i)+1);
        end
        answ=[];
        
        if nbr>1000 then
            msg=["The Hamiltonian has more than "+string(nbr)+" Eigenstates!";...
            "Do you really want to calculate that beast?"];
            answ=messagebox(msg, "modal", "info", ["Yes" "No"]);
        end
        if answ==2 then 
            abort;
        end
    
        if size(atomlink,2)<2 then
            winH=waitbar(0,'Wait for plotting states');
            scf(f);
            [x,y]=Plotstates(atomlink,experiment.B);
            plotdrawn=1;
            waitbar(1,winH);
            close(winH);
        else
            HH=0;
            ////
            //the heisenberg coupling matrix
            JH=experiment.matrix;
            JH1=experiment.heisenberg_coupling;
            
            for i=1:size(JH,1),
                for j=2:size(JH,2)+1,
                    if j>i then
                        HH=HH+HHeisenberg(atomlink,evstr(JH(i,j-1))*JH1,i,j);
                    end
                end
            end
            ////
            ////
            //the DM coupling
            M=experiment.matrixDM;
            J=experiment.heisenberg_coupling;
        
            for i=1:size(M,1),
                for j=2:size(M,2)+1,
                    if j>i then
                        HH=HH+HDM(atomlink,evstr(M(i,j-1))*J,i,j);
                    end
                end
            end
        
            b=linspace(0,1,experiment.no_eval);
            x=b*sqrt(sum(experiment.B.^2));
            clear y;
            winH=waitbar(0,'Wait for plotting states');
            gui_startcalc();
            if size(HH,1) < experiment.max_no_eigenstates+2 then
                for i=1:experiment.no_eval,
                    H=full(HAni(atomlink,b(i)*experiment.B)+HH);
                    y(:,i)=spec(H);
                    if %zeroadj then
                        y(:,i)=y(:,i)-min(y(:,i));
                    end
                    if ~%stopcalc then
                        waitbar(i/experiment.no_eval,winH);
                    else
                        close(winH);
                        gui_stopcalc();
                        return;    
                    end
                    
                end,
            else
                for i=1:experiment.no_eval,
                    H=HAni(atomlink,b(i)*experiment.B)+HH;
                     ofst=0;ofstold=0;
                     while ofst >= 0
                        H=H-ofst*speye(H); /////
                        [vcn,Cn]=eigs(H,speye(H),experiment.max_no_eigenstates);
                        ofstold=ofstold+ofst;
                        ofst=max(real(diag(vcn)));
                     end
                    y(:,i)=diag(real(vcn))+ofstold;
                    y=gsort(y,'r','i');
                    if %zeroadj then
                        y(:,i)=y(:,i)-min(y(:,i));
                    end
                    if ~%stopcalc then
                        waitbar(i/experiment.no_eval,winH);
                    else
                        close(winH);
                        gui_stopcalc();
                        return;    
                    end
                end,
            end,
            close(winH);
            gui_stopcalc("OK");
        end
        //shorten eventually x when interrupted
        calc.states=[x',y'];
    end
    
    scf(f);
    if plotdrawn==0 then
        plot(calc.states(:,1),calc.states(:,2:$));
    end
    gui.graph_ui.x_label.text="B (T)";
    gui.graph_ui.y_label.text="E (meV)";
    gui.graph_ui.data_bounds=[min(calc.states(:,1)), min(calc.states(:,2: $))..
    ;max(calc.states(:,1)),max(calc.states(:,2:$))];
 
    
endfunction

function gui_eigenstates(),
    
   global experiment calc;
    
   if experiment.Eigenval==[] then
      eigenvalues(experiment);
   end;
   
   [xsize,ysize]=size(experiment.Eigenvec);
   if calc.occ==[] then
       answ=messagebox("Choose the display mode", "modal", "info",..
       ["Colorplot of the states" "Reduced to the giant spin model",...
       "Matrix of Eigenvectors","Negativity"]);
   else
       answ=messagebox("Choose the display mode", "modal", "info",..
       ["Colorplot of the states" "Reduced to the giant spin model",...
       "Matrix of Eigenvectors", "Negativity", "Occupation of the states",...
       "Lifetime of the states","Entropy of the spin system"]);
   end
    
   select answ
   
   case 1 then  //Colorplot of the states
   
       hh=scf();
       temp=hotcolormap(100);
       //temp=jetcolormap(100);
       hh.color_map=temp//temp($:-1:1,:); //invert colorscale
       
       maximum=max(abs(experiment.Eigenvec));
       colorbar(0,maximum);
       hh.children(1).y_label.text="absolute state prefactor";
       Matplot((0*1+abs(experiment.Eigenvec(:,$:-1:1)')/maximum)*99.9,"081");
       //create x-label
       label=[];
       if  xsize<1000 then
           //only draw labels on x-coordinate if the size is reasonable small
           for i=1:xsize,
               str=string(State(experiment.atom,i)');
               label=[label;'$\begin{bmatrix}'+strcat(str(1:$-1)+"\\")+str($)+'\end{bmatrix}$'];
           end
           hh.children(2).x_ticks = tlist(["ticks", "locations", "labels"], (1:xsize)',label);
       end
       
       //create y-labels
       if ysize<1000 then
           //only draw labels on y-coordinate if the size is reasonable small
           format(6);
           str=string(experiment.Eigenval-min(experiment.Eigenval));
           format(10);
           label='$'+str+'$';
           hh.children(2).y_ticks = tlist(["ticks", "locations", "labels"], (1:ysize)',str);
           hh.children(2).y_label.text="E (meV)";
       end    
   
   case 2 then //Reduced to the giant spin model
   
       operatorS2=S2n(experiment.atom);
       answ2=messagebox("Choose quantization axis", "modal", "info",..
       ["X", "Y", "Z","B-field"]);
       select answ2
       case 1 then
          operatorSz=Sxn(experiment.atom);axistext="S_X";
       case 2 then
          operatorSz=Syn(experiment.atom);axistext="S_Y";
       case 3 then
          operatorSz=Szn(experiment.atom);axistext="S_Z";
       case 4 then
          operatorSz=Sarbn(experiment.atom,experiment.B(1),experiment.B(2),experiment.B(3));
          axistext="S_{\vec{B}}";
       else
          abort;
       end
       
       label=[];nSt=[];nSz=[];label2=[];nSt2=[];nSz2=[];
       for i=1:ysize,
           nS2=experiment.Eigenvec(:,i)'*operatorS2*experiment.Eigenvec(:,i);
           nSt2(i)=(sqrt(4*nS2+1)-1)/2;
           nSt(i)=round(nSt2(i)*10)/10;
           nSz2(i)=experiment.Eigenvec(:,i)'*operatorSz*experiment.Eigenvec(:,i);
           nSz(i)=round(nSz2(i)*1000)/1000;
           
       end
       nSz=nSz+10000; //to trick out gsort which will sort only abs()
       [nSt,k]=gsort(nSt); //sort according to largest total Spin:
       nSz=nSz(k); //reorder
       nSz2=nSz2(k);
       nSt2=nSt2(k);
       vcn=experiment.Eigenval(k); //reorder
       for i=1:ysize,
           temp=find(nSt==nSt(i));
           [temp2,k]=gsort(nSz(temp));
           nSz(temp)=nSz(temp(k));
           nSz2(temp)=nSz2(temp(k));
           //nSt(temp)=nSt(temp(k));
           nSt2(temp)=nSt2(temp(k));
           vcn(temp)=vcn(temp(k));
           i=max(temp)+1;
       end
       nSz=nSz-10000;
       format(5);
       for i=1:ysize,
           label=[label;'$\begin{bmatrix}'+string(nSt(i))+"\\"+string(nSz(i))+'\end{bmatrix}$'];
           label2=[label2;[vcn(i)-min(vcn),nSt2(i),nSz2(i)]];
       end;
       hh=scf();
       calc.giantspin=label2;
       calc.giantspin_label=['Energy','S_total', axistext];
       plot(vcn-min(vcn),'-b.');
       hh.children.x_ticks = tlist(["ticks", "locations", "labels"], (1:ysize)',label);
       hh.children.x_label.text="$\begin{bmatrix}\left< S_{total} \right> \left<"+axistext+"\right> \end{bmatrix}$";
       hh.children.y_label.text="E (meV)";
       hh.children.margins=[0.125 0.125 0.125 0.25];
       format(10);
       xgrid(5);
        
   case 3 then //Matrix of Eigenvectors
   
       Eigenvalues=experiment.Eigenval;
       Eigenvectors=experiment.Eigenvec;
        
       editvar('Eigenvectors');
       editvar('Eigenvalues');
       
   case 4 then //Negativity
       
       if size(experiment.atom,2) < 2 then
         messagebox("For entanglement you need at least two coupled spins");
         abort;
       end
       
       occ=Occupation(experiment.Eigenval,experiment.T);

       rho=[];
       for i=1:length(occ),
          if occ(i)>%precission then
            rho=rho+occ(i)*experiment.Eigenvec(:,i)*experiment.Eigenvec(:,i)';
          end
       end
       neg=negativity(rho,experiment.atom);
       xaxis=[1:size(experiment.atom,2)]';
       hh=scf();
       plot(xaxis,neg,'o-');
       xlabel("atom number");
       ylabel("negativity");
       calc.negativity=[xaxis,neg];
       
   case 5 then //Occupation of the states
       
       hh=scf();
       plot(calc.occ(:,1),calc.occ(:,2:$));
       xlabel("eV (meV)");
       ylabel("State occupation");

   case 6 then //Lifetime of the states
    
    hh=scf();
    plot2d('nl',calc.lifetime(:,1),calc.lifetime(:,2:$));
    xlabel("eV (mV)");
    ylabel("lifetime (s)");
    
   case 7 then //Entropy of the spin system
    hh=scf();
    vnent=[];
    for i=1:size(calc.occ,1),
        //vnent(i)=entropy(diag(gui.user_data_occ(i,2:$)));
        tmp=-calc.occ(i,2:$).*log(calc.occ(i,2:$));
        tmp(isnan(tmp))=0;  //replace %nan with 0
        vnent(i)=sum(tmp);
    end;
    calc.entropy=[calc.occ(:,1),vnent];
    plot(calc.occ(:,1),vnent);
    xlabel("eV (mV)");
    ylabel("entropy (k_B)");    
   end;
    
endfunction

function gui_limits(),
    global minvalues1 maxvalues1 labels1;
    
    labelh=["min";"max"];
    val=string([minvalues1(1:12);maxvalues1(1:12)]');
    newval=x_mdialog('Set boundaries of the parameters',labels1(1:12),labelh,val);
    
    if ~and(newval==val) then
       newval(~isnum(newval))=val(~isnum(newval)); //replace bullshit and set it to old value  
       minvalues1(1:12)=evstr(newval(:,1))';
       maxvalues1(1:12)=evstr(newval(:,2))';
    end
    update_slider();
    
endfunction

function gui_del(),
    
    global gui;
    if gui.graph_ui.visible=='off' then
        gui.graph_ui.visible='on';
    else
        if gui.graph_ui.children<>[] then
           delete(gui.graph_ui.children(1))
        end
    end
    
endfunction

function gui_del_all(),
    
    global gui %Data Data_fname;
    gui.graph_ui.visible='on';
    nbrofplts=size(gui.graph_ui.children,1)
    if gui.graph_ui.children<>[] then
       gui.graph_ui.data_bounds=[0,0;0,0];
       delete(gui.graph_ui.children);
    end
    if size(%Data,1)>1 & nbrofplts>2 then
      scf(f);
      nr=size(%Data,2)-1;
      plot2d(%Data(:,1),%Data(:,2:$),linspace(-9,-9,nr));
      gui.graph_ui.children(1).children.mark_foreground=2;
      gui.graph_ui.children(1).children.mark_size_unit='point';
      gui.graph_ui.children(1).children.mark_size=4;
      captions(gui.graph_ui.children(1).children(1), Data_fname);
    elseif size(%Data,1)>1 then
      mssg=messagebox("Do you really want to remove the experimental data?"..
      ,"modal", "question", ["Yes" "No"]);
      if mssg==1 then
          %Data=[];
      else
          scf(f);
          nr=size(%Data,2)-1;
          plot2d(%Data(:,1),%Data(:,2:$),linspace(-9,-9,nr));
          gui.graph_ui.children(1).children.mark_foreground=2;
          gui.graph_ui.children(1).children.mark_size_unit='point';
          gui.graph_ui.children(1).children.mark_size=4;
          captions(gui.graph_ui.children(1).children(1), Data_fname);  
      end
    end
    
endfunction

function gui_save(),
    
    global gui experiment %Data;
    
     answ=messagebox("What do you want to save", "modal", "info",..
       ["Program Status" "Export Calculation"]);
    
    if answ==1 then
        filename=uiputfile("*.SOD");
        if filename<>"" then
            save(filename,'experiment','calc');
        end
    else
    
        tempexp=[];
        text=fieldnames(experiment);
        for i=1:size(text,1),
            if text(i)<>"Eigenvec" & text(i)<>"Eigenval" then
               execstr("tempexp."+text(i)+"=experiment."+text(i));              
            end;
        end;
        
        text=string(tempexp);
                
        atomlink=experiment.atom;
            
        if size(atomlink,2)>1 then
           tmp=experiment.matrix;
           text=[text;'Heisenberg Matrixvalues:']
           for i=1:size(tmp,2),
               str=' ';
               for j=1:size(tmp,1),
                   str=str+tmp(i,j)+';';
               end
               text=[text;str];
           end
           tmp=experiment.matrixDM;
           text=[text;'DM Matrixvalues:']
           for i=1:size(tmp,2),
               str=' ';
               for j=1:size(tmp,1),
                   str=str+tmp(i,j)+';';
               end
               text=[text;str];
           end
        end
            
        for i=1:size(atomlink,2)
            text=[text;"Spin "+string(i)+":"];
            text=[text;string(atomlink(i))];
        end
        
        dataexist=[];
        for i=1:7,
           dataexist(i)=getfield(i+2,calc)<>[];
        end
        
        labelpos=['Spectrum','States versus B','Occupation of States',..
        'Lifetime of States','Entropy of System','Giant Spin Approximation',..
        'Negativity'];
        
        label=labelpos(dataexist);
        if label==[] then 
            messagebox("No calculated data to save");
            abort;
        end
        
        answ=messagebox("Which data do you want to save", "modal", "info",label);
        
        if answ==0 then abort, end; 
        
        pos=find(dataexist==%T);
        data=getfield(pos(answ)+2,calc); //extract data
        
        filename=uiputfile("*.dat");
        if filename<>"" then
            savedat(filename,data($:-1:1,1),real(data($:-1:1,2:$)),text);
        end;
    end;
endfunction


function gui_load(),

    global f %Data guientry1 guicheckbox1 experiment gui PATH Data_fname;
    
    
    
    if exists('IBM_import') then
        answ=messagebox("What do you want to load", "modal", "info",..
       ["Program Status" "ASCII Data" "IBM Data"]);
    else
        answ=messagebox("What do you want to load", "modal", "info",..
       ["Program Status" "ASCII Data"]);
    end
     
     select answ
     
     case 1 then  
        [filename,filedir]=uigetfile("*.SOD",PATH);
        if filename<>"" then
            err=execstr("load(filedir+''/''+filename,''experiment'',''calc'')",'errcatch');
            if err then
                // old SOD file prior version 0.991
                disp('old SOD file prior version 0.991')
                load(filedir+'/'+filename,'experiment','atomlink');
                //check if DM interaction is included to be compatible
                if ~or(getfield(1,experiment)=='matrixDM') then
                experiment.matrixDM='0, 0, 0';
                end;
            end;
            txt=getfield(1,experiment);
            //check if paramag_S is included to be compatible
            if grep(txt,'paramag_S')==[] then
                experiment.paramag_S=5/2;
            end
            //adapt size of experiment.sw to be compatible
            
            if length(experiment.sw)>13 then 
                experiment.sw(5:13)=experiment.sw(6:14); 
                //to account for version 0.999
            end
            
            experiment.sw(length(experiment.sw)+1:13)=%T;
            experiment.sw=experiment.sw(1:13);
            
            PATH=filedir;
            
            for k=1:length(experiment.sw),
                guicheckbox1(k).value=1*(~experiment.sw(k));
            end
           
            update_gui_values();
            number_spins_callback();
            checkbox1_callback();
            cleardata(2);   //clear all calculation
        end
    
     case 2 then  
        [Data_fname,filedir]=uigetfile("*.dat",PATH);
        if Data_fname<>"" then
            fn=mopen(filedir+'/'+Data_fname);
            txt = mgetl(fn);
            dat=[];
            PATH=filedir;
            for i=1:size(txt,1),
                [a,err]=evstr(txt(i));
                if err==0 then
                   dat=[dat;a];
                end,
            end
            mclose(fn);
            if size(dat,2)> 2 then
                text=["Data has more than two columns.";..
                "Extracting Data from column "+..
                gui.sel_Load_Row.String+" ?"];
                answ2=messagebox(text, "modal", "info",..
                ["Yes" "No"]);
                if answ2==1 then
                    %Data=[1000*dat(:,1),dat(:,abs(evstr(gui.sel_Load_Row.String)))];
                    if evstr(gui.sel_Load_Row.String)<0 then
                        %Data(:,2)=-%Data(:,2); //invert the data
                    end;
                else
                    %Data=[dat(:,1),dat(:,2:$)];
                end
            else
                %Data=[dat(:,1),dat(:,2)];
            end;
            scf(f);
            nr=size(%Data,2)-1;
            plot2d(%Data(:,1),%Data(:,2:$),linspace(-9,-9,nr));
            
            
            
            gui.graph_ui.children(1).children.mark_foreground=2;
            gui.graph_ui.children(1).children.mark_size_unit='point';
            gui.graph_ui.children(1).children.mark_size=4;
            captions(gui.graph_ui.children(1).children(1), Data_fname);
            
            if nr==1 then
               guientry1(16).String=string(max(abs(%Data(:,1))));
            else
               guientry1(13).String=string(max(abs(%Data(:,1))));
               guientry1(14).String="0"; 
               guientry1(15).String="0";
            end
            entry1_callback();
            //update_gui_values();
            //update_atomlink();
        end
        
    case 3 then  
        [filename,filedir]=uigetfile("*.*",PATH);
        if filename<>"" then
            [%Data,Header]=IBM_import(filedir+'/'+filename);
            %Data(:,1)=%Data(:,1)*1000; //rescale to mV
            scf(f);
            PATH=filedir;
            plot2d(%Data(:,1),%Data(:,2)),-9;
            guientry1(15).String=string(max(abs(%Data(:,1))));
            gui.graph_ui.children(1).children.mark_foreground=2;
            gui.graph_ui.children(1).children.mark_size_unit='point';
            gui.graph_ui.children(1).children.mark_size=4;
            entry1_callback();
            //update_gui_values();
            //update_atomlink();
        end;
    end
endfunction

function udata(S),
    
    global experiment ;

    number=gui.sel_spin2.Value;
    experiment.atom(number).S=S.S;
    experiment.atom(number).g=S.g;
    experiment.atom(number).D=S.D;
    experiment.atom(number).E=S.E;
    experiment.atom(number).U=S.U;
    experiment.atom(number).J=S.J;
    experiment.atom(number).w=S.w;
    
    cleardata(2);
    update_gui_values();
    update_atomlink();
    
endfunction

function gui_parameters(),
    
    global experiment %savedata %plotspec %precission %normalize %zeroadj;
    
    txt = ['Max # of eigensstates';'Gamma (meV)';'Min state occupancy';..
    '# of evaluations';'Save all data immediatelly';..
    'Plot all spectra';'Normalize data';'Adjust states to zero'];
    sig=[string(experiment.max_no_eigenstates);string(experiment.lt);..
    string(%precission);string(experiment.no_eval);string(%savedata);..
    string(%plotspec);string(%normalize);string(%zeroadj)];
    
    answ = x_mdialog('Modify some global parameter. BE CAREFULL!',txt,sig);
    if answ==[] then
        answ=sig;
    end
    answ(~isnum(answ(1:4)))='1'; //replace bullshit
    
    if experiment.max_no_eigenstates <> evstr(answ(1)) then
        experiment.max_no_eigenstates = evstr(answ(1));
        cleardata(2);
    end;
    if experiment.lt <> evstr(answ(2)) then
        experiment.lt = evstr(answ(2));
        cleardata(1);
    end
    if %precission <> evstr(answ(3)) then
        %precission = evstr(answ(3));
        cleardata(1);
    end
    
    if experiment.no_eval <> evstr(answ(4)) then
        experiment.no_eval = evstr(answ(4));
        cleardata(2);
    end
    
    old=%savedata;
    if answ(5)=='%T'|answ(5)=='%t'|answ(5)=='T' then 
        %savedata=%T
    else
        %savedata=%F;
    end
    if old<>%savedata then cleardata(1),end;
        
    old=%plotspec;    
    if answ(6)=='%T'|answ(6)=='%t'|answ(6)=='T' then 
       %plotspec=%T; 
    else
       %plotspec=%F;
    end
    if old<>%plotspec then cleardata(1),end;
    
    old=%normalize;
    if answ(7)=='%T'|answ(7)=='%t'|answ(7)=='T' then 
       %normalize=%T
    else
       %normalize=%F;
    end
    if old<>%normalize then cleardata(1),end;
    
    old=%zeroadj;
    if answ(8)=='%T'|answ(8)=='%t'|answ(8)=='T' then 
       %zeroadj=%T;
    else
       %zeroadj=%F;
    end
    if old<>%zeroadj then cleardata(2),end;

endfunction

function gui_switchexp()
    
    global experiment experiment2 guicheckbox1 guientry1 guislider1 gui calc;
    
    temp=experiment;
    experiment=experiment2;
    experiment2=temp;
    
    update_gui_values();
    number_spins_callback();
    
    cleardata(2);   //clear all calculation
    
endfunction

function gui_checkanisotropy()

    global experiment guicheckbox1 guientry1 guislider1 gui gh;
    number=gui.sel_spin2.Value;
    S.D=experiment.atom(number).D;
    S.E=experiment.atom(number).E;
    badDE=~(3*abs(S.E)<abs(S.D) & S.E>=0);
    SS=Dxyz(S);
    
    ierr = execstr("close(gh)", "errcatch");
    gh=figure('figure_position',[1000,0],'figure_size',[500,700],'auto_resize',..
   'on','figure_name',..
   '3rd order tunneling simulator. (c) Markus Ternes ');

    gh.color_map = coolcolormap(128);
    gh.background=-2
    hh.data=[];
    hh.graph_ui=newaxes();
    hh.graph_ui.margins=[0 0 0 0.0];
    hh.graph_ui.axes_bounds=[0.05,0.05,0.9,0.9];
  
    subplot(211);
    w=gcf();
    w.children(1).axes_bounds=[0 0 1 0.6];
    //drawanisotropy(S);
    nr=2*(experiment.atom(number).S)+1;
    H=HAni(experiment.atom(number),experiment.B);
    tempEigenval=spec(H);

    //dm=Occupation(tempEigenval,experiment.T);
    dm=zeros(tempEigenval); dm(1,1)=1;
    
    drawanisotropy(H,diag(dm));
    //drawanisotropy(HAni(experiment.atom(number),experiment.B),nr);
    
    subplot(212);
    str=["$\mbox{The anisotropy parameters:}$";"$D="+string(S.D)+", E="+..
    string(S.E)+"$";"$\mbox{correspond to}$";"$D_{xx}="+string(SS.Dxx)+..
    ", D_{yy}="+string(SS.Dyy)+", D_{zz}="+string(SS.Dzz)+"$"];
    
    SN.Dxx=SS.Dyy;SN.Dyy=SS.Dxx;SN.Dzz=SS.Dzz;
    SN=Dde(SN);
    if 3*abs(SN.E)<abs(SN.D) & badDE then
        str=[str;"$\bf \quad\mbox{Flipping }x \rightleftharpoons y\mbox{ axes results in}$";..
        "$\bf D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];
    else 
        str=[str;"$\quad\mbox{Flipping }x \rightleftharpoons y\mbox{ axes results in}$";..
        "$D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];

    end
    
    SN.Dxx=SS.Dzz;SN.Dzz=SS.Dxx;SN.Dyy=SS.Dyy;
    SN=Dde(SN);
    if 3*abs(SN.E)<abs(SN.D) & badDE then
        str=[str;"$\bf \quad\mbox{Flipping }x \rightleftharpoons z\mbox{ axes results in}$";..
    "$\bf D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];
    else 
        str=[str;"$\quad\mbox{Flipping }x \rightleftharpoons z\mbox{ axes results in}$";..
    "$D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];
    end
    

    SN.Dyy=SS.Dzz;SN.Dzz=SS.Dyy;SN.Dxx=SS.Dxx;
    SN=Dde(SN);
    if 3*abs(SN.E)<abs(SN.D) & badDE then
        str=[str;"$\bf \quad\mbox{Flipping }y \rightleftharpoons z\mbox{ axes results in}$";..
        "$\bf D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];
    else 
        str=[str;"$\quad\mbox{Flipping }y \rightleftharpoons z\mbox{ axes results in}$";..
        "$D="+string(SN.D)+", E="+string(SN.E)+"\quad$"];
    end

    hh.button_change = uicontrol("parent",gh, "style","pushbutton", ...
    "Position",[60 10 100 25], "String","Flip the axes", ...
    "BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
    "Relief","raised",...
    "TooltipString", "Flip the anisotropy axes with respect to the main (magnetic) axes", ...
    "Callback","flip_axes()");

    hh.button_change = uicontrol("parent",gh, "style","pushbutton", ...
    "Position",[200 10 100 25], "String","Enter Dnn", ...
    "BackgroundColor",[0.6,0.9,0.9], "fontsize",11, ...
    "Relief","raised",...
    "TooltipString", "Enter Anisotropy parameters directly (see PRL111,127203)", ...
    "Callback","enter_dnn()");

    hh.button_ok = uicontrol("parent",gh, "style","pushbutton", ...
   "Position",[340 10 100 25], "String","OK", ...
   "BackgroundColor",[0.6,0.9,0.6], "fontsize",11, ...
   "Relief","raised",...
   "TooltipString", "Close submenu", ...
   "Callback","close(gh)");

   for i=1:size(str,1),
       uicontrol("parent",gh, "style","text", ...
       "Position",[50 235-18*i 400 25], "String",str(i), ...
       "HorizontalAlignment","center",...
       "BackgroundColor",[1,1,1],...
       "fontsize",12);
   end
    //titlepage(str);
    
endfunction

function enter_dnn()
    
    global experiment guicheckbox1 guientry1 guislider1 gui h;
    number=gui.sel_spin2.Value
    S.D=experiment.atom(number).D;
    S.E=experiment.atom(number).E;
    SS=Dxyz(S);

    label=["Dxx";"Dyy";"Dzz";"lambda"];
    str=string([SS.Dxx;SS.Dyy;SS.Dzz;1]);
    new=x_mdialog("Enter Dnn",label,str);
    if size(new)==[4,1] then
       new(~isnum(new))='1'; //replace bullshit and set it to '0'  
       if or(new<>str) then
          lambda=evstr(new(4));
          if lambda<>1 then
              lambda=-lambda^2;
          end
          SS.Dxx=evstr(new(1))*lambda;
          SS.Dyy=evstr(new(2))*lambda;
          SS.Dzz=evstr(new(3))*lambda;
          SN=Dde(SS);
          experiment.atom(number).D=SN.D;
          experiment.atom(number).E=SN.E;
       end
    end
   
    update_gui_values();
    update_atomlink();
    
endfunction

function flip_axes(),

    global experiment guicheckbox1 guientry1 guislider1 gui h;
    number=gui.sel_spin2.Value
    S.D=experiment.atom(number).D;
    S.E=experiment.atom(number).E;
    SS=Dxyz(S);
    flip= messagebox("Which axes you want to flip?", "modal","question",..
    ["x-y","x-z","y-z","none"]);
    select flip
        case 1 then
            SN.Dxx=SS.Dyy;SN.Dyy=SS.Dxx;SN.Dzz=SS.Dzz;
            SN=Dde(SN);
            experiment.atom(number).D=SN.D;
            experiment.atom(number).E=SN.E;
        case 2 then
            SN.Dxx=SS.Dzz;SN.Dzz=SS.Dxx;SN.Dyy=SS.Dyy;
            SN=Dde(SN);
            experiment.atom(number).D=SN.D;
            experiment.atom(number).E=SN.E;
        case 3 then
            SN.Dyy=SS.Dzz;SN.Dzz=SS.Dyy;SN.Dxx=SS.Dxx;
            SN=Dde(SN);    
            experiment.atom(number).D=SN.D;
            experiment.atom(number).E=SN.E;
    end

    update_gui_values();
    update_atomlink();
    
endfunction

addmenu(f.figure_id,'Examples',..
['M449/Au(111)';'Spin-1';'Fe/CuN';'Mn/CuN';'Co/CuN']);
Examples_0=['S.S=0.5;S.g=1.97;S.D=0;S.E=0;S.U=0;S.J=-0.04;S.w=20;udata(S)';..
'S.S=1;S.g=2;S.D=-5;S.E=1;S.U=0.0;S.J=-0.1;S.w=20;udata(S)';..
'S.S=2;S.g=2.11;S.D=-1.57;S.E=0.31;S.U=0.35;S.J=-0.087;S.w=20;udata(S)';..
'S.S=5/2;S.g=1.9;S.D=-0.051;S.E=0;S.U=1.3;S.J=-0.029;S.w=20;udata(S)';..
'S.S=3/2;S.g=2;S.D=2.7;S.E=0.5;S.U=0;S.J=-0.25;S.w=20;udata(S)'];

drawnow();

function gui_exit()
    
    global f, g;

    mssg=messagebox("Do you really want to exit ?","modal", "question", ["Yes" "No"]);
    if mssg==1 then
        close(f);
        if exists('g') then 
            ierr=execstr('close(g);','errcatch');
        end;
        disp('bye');
    end

endfunction

update_gui_values(); checkbox1_callback(); number_spins_callback(); // initialize

