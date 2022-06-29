////////////////////////////////////////////////////////////////////////////////
//
//    Spin-fit-fuctions-1.0.sce
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

function gui_fit(),
    
    global %Data %Data_trunc experiment experiment2 calc guicheckbox1 guientry1 guislider1 gui old_k;

    //check if we have data
    if %Data==[] then 
        messagebox('No data to fit!', 'Attention!', "warning");
        abort;
    end;
    
    if size(%Data,2)==2 then
        fit_spec();
    else
        fit_states();
    end
endfunction

function fit_states()
        
    global %Data experiment experiment2 calc guicheckbox1 guientry1 guislider1 minvalues1 maxvalues1 gui;
    
    if size(%Data,2)>(2*experiment.atom.S)+1 then
        messagebox('Spin must be higher!', 'Attention!', "warning");
        abort;
    end
    
    if size(experiment.atom,2)>1 then
        messagebox('This function is not yet supported', 'Attention!', "warning");
        abort;
    end
     
    %Data(:,2:$)=gsort(%Data(:,2:$),'c','i');
        // menue
    sig = x_mdialog('Fit parameter',..
    ['maximum number of calls';'maximum number of iterations'],['100';'50']);
    if prod(size(sig)<>[2,1]) then
        abort;
    end;
    
    atom=experiment.atom(experiment.position);
    i=1;
    fitmin=[];
    fitmax=[];
    if experiment.sw(1) then
       k(i)=atom.g;i=i+1;
       fitmin=[fitmin;minvalues1(1)];
       fitmax=[fitmax;maxvalues1(1)];
    end
    if experiment.sw(2) then
       k(i)=atom.D;i=i+1;
       fitmin=[fitmin;minvalues1(2)];
       fitmax=[fitmax;maxvalues1(2)];
    end
    if experiment.sw(3) then
       k(i)=atom.E;i=i+1;
       fitmin=[fitmin;minvalues1(3)];
       fitmax=[fitmax;maxvalues1(3)];
    end
    
    k0=k;
    winId=progressionbar('Fitting. Please be patient!');
    
    //[fopt,k,gopt]=leastsq(imp=2,diff_states, k0,"ar",evstr(sig(1)),evstr(sig(2)));
    [fopt,k,gopt]=leastsq(imp=2,diff_states,"b",fitmin,fitmax,k0,"ar",evstr(sig(1)),evstr(sig(2)));
    close(winId);
    
    atom=experiment.atom(experiment.position);
    i=1
    if experiment.sw(1) then
       atom.g=k(i);i=i+1;
    end
    if experiment.sw(2) then
       atom.D=k(i);i=i+1;
    end
    if experiment.sw(3) then
       atom.E=k(i);i=i+1;
    end
    
    experiment.atom(experiment.position)=atom;
    experiment2=experiment;
    gui_switchexp();
    cleardata(2);   //clear all calculation
    gui_drawstates();
        
endfunction

function out=diff_states(k),
    
    global %Data experiment;
    
    atom=experiment.atom;
    i=1;
    if experiment.sw(1) then
       atom.g=k(i);i=i+1;
    end
    if experiment.sw(2) then
       atom.D=k(i);i=i+1;
    end
    if experiment.sw(3) then
       atom.E=k(i);i=i+1;
    end
    
    out=[];
    for Bz=1:size(%Data,1),
        B=[0,0,%Data(Bz,1)];
        
        [M,vm]=spec(HZ(atom,B)+Haniso(atom));
        eigenval=diag(vm);
        eigenval=eigenval-min(eigenval);
        for i=2:size(%Data,2),
            out=[out;%Data(Bz,i)-eigenval(i)];
        end
    end
    
endfunction

function [k,fitmin,fitmax]=exp_to_k(experiment),
    
    global minvalues1 maxvalues1;
    
    i=1;k=[];fitmin=[];fitmax=[];
    atom=experiment.atom(experiment.position);
    
    if experiment.sw(1) then
       k(i)=atom.g;i=i+1;
       fitmin=[fitmin;minvalues1(1)];
       fitmax=[fitmax;maxvalues1(1)];
    end
    if experiment.sw(2) then
       k(i)=atom.D;i=i+1;
       fitmin=[fitmin;minvalues1(2)];
       fitmax=[fitmax;maxvalues1(2)];

    end
    if experiment.sw(3) then
       k(i)=atom.E;i=i+1;
       fitmin=[fitmin;minvalues1(3)];
       fitmax=[fitmax;maxvalues1(3)];

    end
    if size(experiment.atom,2) >1 & experiment.sw(13) then
       k(i)=experiment.heisenberg_coupling;
       fitmin=[fitmin;-%inf];
       fitmax=[fitmax;+%inf];

       i=i+1;
    end
    if experiment.sw(4) then  
       k(i)=atom.U;i=i+1;
       fitmin=[fitmin;minvalues1(4)];
       fitmax=[fitmax;maxvalues1(4)];

    end
    if experiment.sw(5) then
       k(i)=atom.J;i=i+1;
       fitmin=[fitmin;minvalues1(5)];
       fitmax=[fitmax;maxvalues1(5)];

    end
    if experiment.sw(6) then
       k(i)=atom.w;i=i+1;
       fitmin=[fitmin;minvalues1(6)];
       fitmax=[fitmax;maxvalues1(6)];

    end
    if experiment.sw(9) then
       k(i)=experiment.x0;i=i+1;
       fitmin=[fitmin;minvalues1(9)];
       fitmax=[fitmax;maxvalues1(9)];

    end
    if experiment.sw(11) then
       k(i)=experiment.T;i=i+1;
       fitmin=[fitmin;minvalues1(11)];
       fitmax=[fitmax;maxvalues1(11)];

    end
    if experiment.sw(12) & sum(experiment.B.^2)<>0 & sum(experiment.ptip.^2)<>0 then
       //calculate angle between B and ptip
       angle=real(acos((experiment.ptip*experiment.B')/...
       (sqrt(sum(experiment.ptip.^2))*sqrt(sum(experiment.B.^2)))));
       //if angle is larger than 90 deg eta<0
       //eta is the length of experiment.ptip
       if angle>%pi/2 then
          k(i)=-sqrt(sum(experiment.ptip.^2));
       else
          k(i)=sqrt(sum(experiment.ptip.^2));
       end
       i=i+1;
       fitmin=[fitmin;minvalues1(12)];
       fitmax=[fitmax;maxvalues1(12)];

    end
    if experiment.sw(7) then
       k(i)=experiment.A;i=i+1;
       fitmin=[fitmin;minvalues1(7)];
       fitmax=[fitmax;maxvalues1(7)];

    end
    if experiment.sw(8) then
       k(i)=experiment.b;i=i+1;
       fitmin=[fitmin;minvalues1(8)];
       fitmax=[fitmax;maxvalues1(8)];

    end
    if experiment.sw(10) then
       k(i)=experiment.y0;i=i+1;
       fitmin=[fitmin;minvalues1(10)];
       fitmax=[fitmax;maxvalues1(10)];

    end
    
endfunction

function [experiment]=k_to_exp(k,experiment),
    
    atom=experiment.atom(experiment.position);
    i=1;
    if experiment.sw(1) then
       atom.g=k(i);i=i+1;
    end
    if experiment.sw(2) then
       atom.D=k(i);i=i+1;
    end
    if experiment.sw(3) then
       atom.E=k(i);i=i+1;
    end
    if size(experiment.atom,2) >1 & experiment.sw(13) then
       experiment.heisenberg_coupling=k(i);
       i=i+1;
    end
    if experiment.sw(4) then
       atom.U=k(i);i=i+1;
    end
    if experiment.sw(5) then
       atom.J=k(i);i=i+1;
    end
    if experiment.sw(6) then
       atom.w=k(i);i=i+1;
    end
    if experiment.sw(9) then
       experiment.x0=k(i);i=i+1;
    end
    if experiment.sw(11) then
       experiment.T=k(i);i=i+1;
    end
    if experiment.sw(12) & sum(experiment.B.^2) <>0 & sum(experiment.ptip.^2)<>0 then
       angle=real(acos((experiment.ptip*experiment.B')/...
       (sqrt(sum(experiment.ptip.^2))*sqrt(sum(experiment.B.^2)))));
       sig=1-2*(angle>%pi/2); //if angle>pi/2 then sig=-1, else +1
       experiment.ptip=experiment.ptip/sqrt(sum(experiment.ptip.^2))*k(i)*sig;
       i=i+1;
    end
    if experiment.sw(7) then
       experiment.A=k(i);i=i+1;
    end
    if experiment.sw(8) then
       experiment.b=k(i);i=i+1;
    end
    if experiment.sw(10) then
       experiment.y0=k(i);i=i+1;
    end
        
    experiment.atom(experiment.position)=atom;
    
endfunction

function k=fit_spec(varargin),
    
    global %Data %Data_trunc experiment experiment2 calc old_k itcount gui minvalues1 maxvalues1;

    experiment2=experiment;
    //truncate data if neccessary
    if max(abs(%Data(:,1)))>experiment.xrange then
        %Data_trunc=%Data(find(abs(%Data(:,1))<=experiment.xrange),:)
    else
        %Data_trunc=%Data;
    end
    
    [lhs,rhs]=argn(0); 
    
    if rhs < 2 then  
        // ask for number of iteration menue
        sig = x_mdialog('Fit parameter',..
        ['maximum number of calls';'maximum number of iterations'],['100';'50']);
        if prod(size(sig)<>[2,1]) then
            abort;
        end;
        sig(~isnum(sig))='10'; //replace bullshit
        sig=[evstr(sig(1)),evstr(sig(2))];
    else
        sig=[varargin(1),varargin(2)];
    end
    experiment.position=gui.sel_spin2.value;
    experiment.jposition=experiment.position;
    
    experiment.allatomsequ=gui.allatomsequ.Value;
    
    [k,fitmin,fitmax]=exp_to_k(experiment);
    
    k0=k;old_k=[];calc.spec_raw=[];
    
    fst=create_f_fit(experiment);
    //disp(k0);
    execstr(fst);
    
    function [fk,dfk,ind]=costfkt(k,ind),
        global %Data_trunc experiment old_k calc itcount;
        if %stopcalc then
            fk=0;
            dfk=zeros(k);
            return;
        end  
                  
        fk=f_fit(k);itcount(3)=fk;
//        dfk=numdiff(f_fit,k);           //is this a good way???
        dfk=numderivative(f_fit,k);           //is this a good way???
        if exists('itcount') then
            itcount(1)=itcount(1)+1;
        else
            itcount=[1,1,0];
        end;
    endfunction

    
    itcount=[0,0,0];
    gui_disable();
    tic();
    winId=progressionbar('Fitting. Please be patient!');
    gui_startcalc();

//   [fopt, k, gopt] = optim(costfkt, k0,"ar",sig(1),sig(2),imp=2);
    disp([fitmin,k,fitmax]);
   [fopt, k, gopt] = optim(costfkt, "b", fitmin, fitmax, k0,"ar",sig(1),sig(2),imp=2);
    close(winId);
    
    fopt=f_fit(k);
    if rhs <> 2 then
        messagebox(['Fitting finshed!';..
           'Elapsed time: '+string(toc())+' s';..
           'No of calls: '+string(itcount(1));..
           'Error: '+string(fopt)]);
    end;
    gui_stopcalc();
    experiment=k_to_exp(k,experiment);
    
    experiment.xrange=experiment2.xrange;
   
    update_gui_values();
    gui_enable();
    
    cleardata(2);   //clear all calculation
    gui_drawspec();
    
    gui.graph_ui.children(2).children.foreground=5;
    gui.graph_ui.children(2).children.thickness=2;
    
endfunction

function [fst]=create_f_fit(experiment)
    
    fst=['function [fk]=f_fit(k),';..
    ' ';..
    'global %Data_trunc experiment old_k calc;';..
    'atom=experiment.atom(experiment.position);']
    fst1=[];    //here we have to calculate all new (g,D,E,Jheis)
    fst2=[];    //here we have to recalc 2nd and 3d (spin-pol, T, w, U, J, x0)
    fst3=[];    //here we have to rescale only (A,b,y0)
    
    i=1;
    if experiment.sw(1) then
       fst=[fst;'atom.g=k('+string(i)+')'];
       fst1=['k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(2) then
       fst=[fst;'atom.D=k('+string(i)+')'];
       fst1=[fst1;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(3) then
       fst=[fst;'atom.E=k('+string(i)+')'];
       fst1=[fst1;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(13) & size(experiment.atom,2) >1 then
       fst=[fst;'experiment.heisenberg_coupling=k('+string(i)+');'];
       fst1=[fst1;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    
    if experiment.sw(4) then
       fst=[fst;'atom.U=k('+string(i)+')'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(5) then
       fst=[fst;'atom.J=k('+string(i)+')'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(6) then
       fst=[fst;'atom.w=k('+string(i)+')'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(9) then
       fst=[fst;'experiment.x0=k('+string(i)+')'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(11) then
       fst=[fst;'experiment.T=k('+string(i)+')'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(12) & sum(experiment.B.^2) <> 0 & sum(experiment.ptip.^2)<>0 then
       fst=[fst;'angle=real(acos((experiment.ptip*experiment.B'')/(sqrt(sum(experiment.ptip.^2))*sqrt(sum(experiment.B.^2)))));'];
       fst=[fst;'sig=1-2*(angle>%pi/2);'];
       fst=[fst;'experiment.ptip=experiment.ptip/sqrt(sum(experiment.ptip.^2))*k('+string(i)+')*sig;'];
       fst2=[fst2;'k('+string(i)+')<>old_k('+string(i)+')'];
       i=i+1;
    end

    if experiment.sw(7) then
       fst=[fst;'experiment.A=k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(8) then
       fst=[fst;'experiment.b=k('+string(i)+')'];
       i=i+1;
    end
    if experiment.sw(10) then
       fst=[fst;'experiment.y0=k('+string(i)+')'];
       i=i+1;
    end
    
    if fst1<>[] then
        fst1=fst1+'|';
        fst1=strcat(fst1);
    end
    
    if fst2<>[] then
        fst2=fst2+'|';
        fst2=strcat(fst2);
    end
    
    if experiment.allatomsequ==0 then
        fst=[fst;..
        'experiment.atom(experiment.position)=atom;';..
        'c=%F;'];
    else
        fst=[fst;..
        'experiment.atom(:)=atom;';..
        'c=%F;'];
    end

    fst=[fst;..
    'if '+fst1+' experiment.Eigenval==[] then';..
    '   [M,vm]=spec(full(hamiltonian(experiment)));';..
    '   experiment.Eigenvec=M;';..
    '   experiment.Eigenval=vm;';..
    '   c=%T;';..
    'end']
    
    fst=[fst;..
    'if '+fst2+' calc.spec_raw==[] | c then';..
    '   experiment.xrange=%Data_trunc(:,1)-experiment.x0;';..
    '   [x,y]=spec2(experiment);'];
    
    if experiment.third_order_calc then
        fst=[fst;..
        '   occ=Occupation(experiment.Eigenval,experiment.T);'];
        if experiment.entanglement then
            fst=[fst;..
            'for jp=1:size(experiment.atom,2),';..
            'experiment.jposition=jp;'];
        else
            fst=[fst;'experiment.jposition=experiment.position;'];
        end
        fst=[fst;..
        '   for i=1:size(experiment.Eigenvec,2),';..
        '       if occ(i)>%precission then';..
        '           [x,y1,y1r]=spec3(experiment,i);';..
        '            y=y+y1+y1r;';..
        '       end,';..
        '   end'];
        if experiment.entanglement then
            fst=[fst;'end;'];
        end;
    end

    fst=[fst;..
    '    calc.spec_raw=[x,y];';..
    'else';..
    '    x=calc.spec_raw(:,1);';..
    '    y=calc.spec_raw(:,2);';..
    'end;'];
    if isdef("%weight") then
        fst=[fst;..
        'fk=sum((%Data_trunc(:,2)-experiment.A*(real(y)+experiment.y0+experiment.b*%Data_trunc(:,1))).^2*%weight);'];
    else
        fst=[fst;..
        'fk=sum((%Data_trunc(:,2)-experiment.A*(real(y)+experiment.y0+experiment.b*%Data_trunc(:,1))).^2);'];
    end

    fst=[fst;..
    'old_k=k;';..
    'endfunction']
    
endfunction
