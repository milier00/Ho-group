////////////////////////////////////////////////////////////////////////////////
//
//    Spin-additional-functions-1.0.sce
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

funcprot(0);
ieee(2)

////////////////////////////////////////////////////////////////////////////////
//some usefull functions
////////////////////////////////////////////////////////////////////////////////

//Appelbaum's functions 

function[e]=AvrgM(S,delta,T)
    // This is the Brillouin function 
    // for example, for S=1/2 it is the same as:
    // +S*Occupation(d,1)+(-S)*Occupation(d,1) with d=[-delta 0; 0 delta]
    e=(2*S.S+1)/(2*S.S)*coth((2*S.S+1)/(2*S.S)*delta/(2*T))-1/(2*S.S)*coth(1/(2*S.S)*delta/(2*T));
endfunction

////////////////////////////////////////////////////////////////////////////////
//some special analytical functions
////////////////////////////////////////////////////////////////////////////////

function[e]=ln_t2(x,e0,T,lt)
    // 'e' is the temperature folded log function
    //
    //   -e0/
    //     [
    //   e=I  f(e',T)/(e-e'+i lt) de' * f'(e,T)
    //     ]
    // +e0/
    //
    // with f(e,T) as the Fermi-Dirac distribution and * as the convolution
    //
    // 'x' is a vector of tunneling voltages
    // 'e0' is the half-bandwidth of the substrate electrons
    // 'T' is the temperature 
    // 'lt' is the lifetime broadening
    
    yspan=x(1)-x($);ycenter=(x(1)+x($))/2;
    i=2*length(x); // i has now 2 times the size of x
    y=linspace(ycenter+yspan,ycenter-yspan,i+1);
    g=log((e0+abs(y-ycenter))./(y-ycenter+lt*%i))+%pi*%i/2;
    z=x/T;
    k=find(abs(z)<1e-3); //values arround zero produce wrong results 
    ez=exp(z);    //k=find(ez==1); ez(k)=1+10^-10;z(k)=10^-10;
    f=-((ez+ez.*(z-1)).*(ez-1).^-2-2*ez.*(ez.*(z-1)+1).*(ez-1).^-3);
    f(k)=1/6;
    f(isnan(f))=0;
    e=2*conv2(f(:),g(:),"same")./(T*i).*abs(yspan);
endfunction

function[e]=ln_t2int(x,e0,T,lt)
    // 'e' is the integrated temperature folded log function
    //
    // 'x' is a vector of tunneling voltages
    // 'e0' is the half-bandwidth of the substrate electrons
    // 'T' is the temperature 
    // 'lt' is the lifetime broadening
    
    yspan=x(1)-x($);ycenter=(x(1)+x($))/2;
    i=2*length(x); // i has now 2 times the size of x
    y=linspace(ycenter+yspan,ycenter-yspan,i+1);
    g=(y-ycenter).*log((e0+abs(y-ycenter))./(y-ycenter+lt*%i))...
    +sign(y-ycenter).*((e0*log(e0+abs(-y+ycenter)))-e0*log(e0)...
    +lt*%i*log(-lt*%i+abs(-y+ycenter))-lt*%i*log(-lt*%i));//+%pi*%i/2;
    z=x/T;
    k=find(abs(z)<1e-3); //values arround zero produce wrong results 
    ez=exp(z);    //k=find(ez==1); ez(k)=1+10^-10;z(k)=10^-10;
    f=-((ez+ez.*(z-1)).*(ez-1).^-2-2*ez.*(ez.*(z-1)+1).*(ez-1).^-3);
    f(k)=1/6;
    f(isnan(f))=0;
    e=2*conv(f,g,"same")./(T*i).*abs(yspan);
    // e is now the integral of ln_t2
    
endfunction

function [e,en]=int_ln_step(x,e0,T,lt,stpos)
    //
    // vd:   peak function
    // v:  integrated peak function
    // u:   step function
    // ud:  differentiated step function
    //
    // int (u*v')=u*v-int(u'*v)
    //
    // this function is NOT working yet...
    // sorry dude... ...math is too hard for me today...
    // if someone knows the result of the 2nd part on the right side...le me know...
    
    vd=ln_t2(x,e0,T,lt); //get vd
    v=ln_t2int(x,e0,T,lt); //get v
    u=fstep((x-stpos)/T); //get u
    
    z=(x-stpos)/T;
    k=find(abs(z)<1e-3); //values arround zero produce wrong results 
    ez=exp(z);    //k=find(ez==1); ez(k)=1+10^-10;z(k)=10^-10;
    ud=-((ez+ez.*(z-1)).*(ez-1).^-2-2*ez.*(ez.*(z-1)+1).*(ez-1).^-3);
    ud(k)=1/6;
    ud(isnan(ud))=0;
    
    
    e=1*v.*u;
    en=v.*ud;   //how do we smartly integrate this part??
    
endfunction

function [e]=Occupation(ve, T),
  // calculate occupation using the Boltzmann distribution
  // ve are the eigenvalues (in meV) 
  // T is the effective temperature (in meV)
  ve=real(ve);
  if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
    ve=diag(ve);
  end
  ve=ve-min(ve);
  if T<>0 then 
      e=exp(-ve/T);
      e=e/sum(e); //check that T<>0
  else 
      bb=size(ve);
      e(1:bb(1))=0; 
      k=min(ve);
      e(find(ve==k))=1;
      e=e./sum(e)
  end
endfunction

function [y]=fstep_simple(x),
   // Fermi-Dirac step function
   y=(exp(x)+1).^-1;
endfunction

function [y]=fstep(x),
    // step function; doubly temperature broadened
    x=clean(x,1e-5); // find all x(i)~0
    z=exp(x);
    y=(1+(x-1).*z)./((z-1).^2);
    y(x==0)=0.5;
    y(isnan(y))=0; //remove the NaN values because of x too large and set them to zero
endfunction

function [y]=fbox(x),
   // Fermi-Dirac box function
   //
   //   +inf/
   //      [
   //    y=I  f(e')*[1-f(e'+x)] de'
   //      ]
   // -inf/
   //
   // with f(e,T) as the Fermi-Dirac distribution 
   x=clean(x,1e-8); //set values <+-1e-8 to zero
   y=x./(1-exp(-x));
   y(isnan(y))=1;
endfunction

function [e]=State(t,n),
    // Gives a list of the mz value of the ensemble t of spins 
    // at the eigenstate number n.
    // State([Fe,Co,...],n)
    
    b=size(t,2);     // determine the number of coupled spins
    e=[];
    for i=1:b,
        m=1;
        for j=1:(i-1), 
            m=m.*.sparse(S1(t(j))); 
        end;
        m=m.*.sparse(Sz(t(i)));
        for j=(i+1):b, 
            m=m.*.sparse(S1(t(j))); 
        end;
        m=full(diag(m));
        e=[e,m(n)];
    end;
endfunction

function [e]=Dde(S),
    //calculate D and E from Dxx,Dyy,Dzz
    S.D=S.Dzz-0.5*(S.Dxx+S.Dyy);
    S.E=0.5*(S.Dxx-S.Dyy);
    e=S;
endfunction

function [e]=Dxyz(S),
    //calculate Dxx,Dyy,Dzz from D and E
    S.Dzz=S.D;
    S.Dxx=S.Dzz-S.D+S.E;
    S.Dyy=S.Dzz-S.D-S.E;
    e=S;
endfunction

function [err]=savedat(name,x,y,text)
   //save the data (x,y)
   rhs=argn(2);
   if (rhs>4) then
     error(58); //incorrect number of arguments
     abort;
   end
  
   if (rhs==3) then
     text=[]; 
   end
  
   if type(name)<>10 then 
       error(55,1); 
       abort;
   end
   [xx,xy]=size(x);
   [yx,yy]=size(y);
 
   if (xx~=1) & (xy~=1) then 
       error(56,2);
       abort; //x is not vector
   end;
   if  xx==1 then 
       x=x'; 
       y=y'; 
       end;

   fo=mopen(name,'w');

   mfprintf(fo,'# Data calculated with a routine written by\n#\n');
   mfprintf(fo,'# Markus Ternes @ MPI Stuttgart\n');
   mfprintf(fo,'#\n');
   mfprintf(fo,'# The calculation was performed on:'+date()+'\n');
   time=getdate();
   mfprintf(fo,'# at:%i:%i:%i\n',time(7),time(8),time(9));
   mfprintf(fo,'#\n');
  
   if text<>[] then
      for i=1:size(text,1),
        mputstr('#'+string(text(i)),fo);
        mfprintf(fo,'\n');  
      end
   end

   for n=1:size(y,2),
     mfprintf(fo,'# set number %f\n', n);
     mfprintf(fo,'#\n');

     for i=1:size(y,1),
        mfprintf(fo,'%e\t%e\n',x(i),y(i,n));
     end;
     mfprintf(fo,'\n');
   end,
   err=mclose(fo);
endfunction

function [c]=crossp(a,b)
    // calculates the crossproduct c=a x b;
    c(1)=a(2)*b(3)-a(3)*b(2);
    c(2)=a(3)*b(1)-a(1)*b(3);
    c(3)=a(1)*b(2)-a(2)*b(1);
endfunction

function [e]=vNentropy(rho),
    // calculates the von Neumann entropy of the density matrix rho 
    if clean(trace(rho^2)-trace(rho))==0 then
        e=0
    else
       a=spec(rho);
       b=log(a);
       b(isnan(b))=0;   //make 0*log(0) equal to 0
       b(isinf(b))=0;   //make 0*log(0) equal to 0
       e=-sum(b.*a)
    end
endfunction

function [e]=negativity(rho,t),
    // calculates the "negativity" of the spin ensemble t,
    // rho is the state vector or the density matrix.
    
    //check if rho is state-vector or density matrix
    if or(size(rho)==1) then
       rho=rho*rho'; 
    end;
    
     b=size(t,2);     // determine the number of coupled spins
     for i=1:b,
         pt=ptranspose(rho,t,i);
         //sp=eigs(pt,speye(pt),50) //what would be a good limit here?
         sp=spec(pt);
         e(i)=sum(abs(real(sp))-real(sp))/2;
     end

endfunction


////////////////////////////////////////////////////////////////////////////////
// Spectrum calculation routines
////////////////////////////////////////////////////////////////////////////////

function [x,y]=spec2(experiment),
    // function to calculate the spectrum in 2nd order
    // experiment has to contain at least the following information:
    //
    // experiment.T         (temperature)
    // experiment.xrange    (xrange or list of x-values)
    // experiment.ptip      (tip spin-polarizaion)
    // experiment.psample   (sample Spin-polarization)
    // experiment.atom      (either the parameters of an atom or a list of atoms)
    // experiment.Eigenvec  (at least two eigenvectors of the Hamiltonian)
    // experiment.Eigenval  (at least two eigenvalues of the Hamiltonian)
    // experiment.position  (the position of the tip when we have a list of atoms)
    //
    // additionally, the following global variables have to be set:
    //
    // %savedata=%T or %F   (if the data should be saved in files directly)
    // %precission=0.001    (lower limit of occupation)
    // %plotspec=%T or %F   (if the data should be plotted directly)
    // 
    // 'x' is a list of the tunneling voltage
    // 'y' is a list of the dI/dV values 

    ve=real(experiment.Eigenval);
    if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
        ve=diag(ve);
    end
    ve=ve-min(real(ve));
    
    occ=Occupation(ve,experiment.T);
    
    //calculate the tunneling transiton matrix with spin-polarization
    rate=Rate2nd2(experiment)';
    rateneg=rate'; 
    
    if isvector(experiment.xrange) then x=experiment.xrange,
        else x=linspace(abs(experiment.xrange),-abs(experiment.xrange),1000)';
    end;
    
    y=[];
    a=size(experiment.Eigenvec);
    for i=1:a(2),
        if occ(i)>%precission then
            for j=1:a(2),
                en=(ve(j)-ve(i)-x)/abs(experiment.T);
                ep=(ve(j)-ve(i)+x)/abs(experiment.T);
                ytemp=occ(i)*(rate(i,j)*fstep(ep)+rateneg(i,j)*fstep(en));
                if %savedata then 
                    csvWrite([x real(ytemp)],..
                    "data"+string(i)+"-"+string(j)+"SF.dat"," ");
                end
                y=y+ytemp;
            end,
        end,
    end;
    
    if %plotspec then 
        gcf(); 
        plot(x,y), 
    end;
    
endfunction

function [x,y,yr]=spec3(experiment,in),
    // function to calculate the spectrum in 3rd order
    // experiment has to contain at least the following information:
    //
    // experiment.T         (temperature)
    // experiment.xrange    (xrange or list of x-values)
    // experiment.lt        (lifetime broadening)
    // experiment.ptip      (tip spin-polarizaion)
    // experiment.psample   (sample spin-polarization)
    // experiment.atom      (either the parameters of an atom or a list of atoms)
    // experiment.Eigenvec  (at least two eigenvectors of the Hamiltonian)
    // experiment.Eigenval  (at least two eigenvalues of the Hamiltonian)
    // experiment.position  (the position of the tip when we have a list of atoms)
    // experiment.jposition (the position where the sample-sample transition takes place)
    //                      (experiment.jposition will be set to experiment.position if not set)
    //
    // additionally, the following global variables have to be set:
    //
    // %savedata=%T or %F   (if the data should be saved in files directly)
    // %precission=0.001    (lower limit of evaluated matrix elements)
    // %plotspec=%T or %F   (if the data should be plotted directly)
    // 
    // 'in' is the initial state number of the calculation
    // 'x' is a list of the tunneling voltage
    // 'y' is a list of the dI/dV values for 'normal' tunneling
    // 'yr' is a list of the dI/dV values for 'time reversed' tunneling
    
    txt=getfield(1,experiment);
    if grep(txt,'jposition')==[] then 
        experiment.jposition=experiment.position;
    end;

    occ=Occupation(real(experiment.Eigenval),experiment.T);
    
    ve=experiment.Eigenval;
    if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
        ve=diag(ve);
    end
    ve=ve-min(real(ve));
    
   [rate,rater,raten,ratenr]=M35(experiment,in);

    if isvector(experiment.xrange) then x=experiment.xrange,
        else x=linspace(abs(experiment.xrange),-abs(experiment.xrange),1000)';
    end;
    
    y=zeros(x);yn=zeros(x);yr=zeros(x);ynr=zeros(x);
    a=size(experiment.Eigenvec);
    for mid=1:a(2),
       for fin=1:a(2),
            if abs(rate(mid,fin))+abs(raten(mid,fin))+...
                abs(rater(mid,fin))+abs(ratenr(mid,fin))>%precission^2 then
                tlog1=ln_t2(ve(mid)-ve(in)+x,..
                experiment.atom(experiment.jposition).w,experiment.T,experiment.lt);
                tlog2=ln_t2(ve(mid)-ve(in)-x,..
                experiment.atom(experiment.jposition).w,experiment.T,experiment.lt);
                
                en=fstep((ve(fin)-ve(in)-x)/experiment.T);
                ep=fstep((ve(fin)-ve(in)+x)/experiment.T);
                
                ytemp=-occ(in)*2*real(rate(mid,fin)*ep.*tlog1);
                ytempn=-occ(in)*2*real(raten(mid,fin)*en.*tlog2);
                
                //temporal reverse                
                ytempr=-occ(in)*2*real(rater(mid,fin)*ep.*tlog2);
                ytempnr=-occ(in)*2*real(ratenr(mid,fin)*en.*tlog1);
                
                if %savedata then 
                    csvWrite([x (ytemp+ytempn)],..
                    "data"+string(in)+"-"+string(mid)+"-"+string(fin)+".dat"," ");
                    csvWrite([x (ytempr+ytempnr)],..
                    "data"+string(in)+"-"+string(mid)+"-"+string(fin)+"r.dat"," ");
                end;
                y=y+ytemp+ytempn;
                //yn=yn+ytempn;
                yr=yr+ytempr+ytempnr;
                //ynr=ynr+ytempnr;
            end;
        end;
    end;
    if %plotspec then 
        plot(x,[real(y),real(yr),real(y+yr)]), 
    end;
endfunction

function [out,outn]=spec3rate(experiment),
    // function to calculate the spectrum in 3rd order WITH RATE EQUATIONS
    // experiment has to contain at least the following informations:
    //
    // experiment.T         (temperature)
    // experiment.xrange    (xrange or list of x-values)
    // experiment.lt        (lifetime broadening)
    // experiment.ptip      (tip spin-polarizaion)
    // experiment.psample   (sample Spin-polarization)
    // experiment.atom      (either the parameters of an atom or a list of atoms)
    // experiment.Eigenvec  (at least two eigenvectors of the Hamiltonian)
    // experiment.Eigenval  (at least two eigenvalues of the Hamiltonian)
    // experiment.position  (the position of the tip when we have a list of atoms)
    // experiment.jposition (the position where the sample-sample transition takes place)
    //                      (experiment.jposition will be set to experiment.position if not set)
    //
    // additionally, the following global variables have to be set:
    //
    // %precission=0.001    (lower limit of evaluated matrix elements)
    // 
    // 'out' is a tensor with [a,a,1000] elements (a=number of eigenstates)
    // and the following meaning:
    // current_ts=out[final-state,initial-state,voltage_Step]
    // current_st=outn[final-state,initial-state,voltage_Step]
    
    if ~exists('%stopcalc') then
        %stopcalc=%F;
    end
    
    txt=getfield(1,experiment);
    if grep(txt,'jposition')==[] then 
        experiment.jposition=experiment.position;
    end;
    
    ve=experiment.Eigenval;
    if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
        ve=diag(ve);
    end
    ve=ve-min(real(ve));

    a=size(experiment.Eigenvec);
    
    if isvector(experiment.xrange) then 
        rnge=max(abs(experiment.xrange)), 
    else
        rnge=(2*experiment.xrange)/999*999.5;
    end;

    x=linspace(rnge,-rnge,2000)';
    
    out=zeros(a(2),a(2),1000); //initilize output matrix
    outn=zeros(a(2),a(2),1000); //initilize output matrix
    
    yspan=(x(1)-x($))/2;ycenter=(x(1)+x($))/2;
    i=length(x); // i has now 2 times the size of x
    y=linspace(ycenter+yspan,ycenter-yspan,i+1);
    //xkernel=fstep_simple(y/experiment.T);
    xkernel=fstep_simple(y/experiment.T);
    
    winH=waitbar('Calculating Spectrum');  
    for in=1:a(2),
       [rate,rater,raten,ratenr]=M35(experiment,in);
       
       if ~%stopcalc then
           waitbar((in-1)/a(2),['Calculating Spectrum';..
           ' ';'Evaluate State '+string(in)+'('+string(a(2))+..
           ') with Spin-Spin Interaction on Atom '+string(experiment.jposition)],winH);
       else
           close(winH);
           return;
       end
       
       
       for fin=1:a(2),
           yp=zeros(x);ypr=zeros(x);
           yn=zeros(x);ynr=zeros(x);
           for mid=1:a(2),
              if abs(rate(mid,fin))+abs(raten(mid,fin))+...
                abs(rater(mid,fin))+abs(ratenr(mid,fin))>%precission^2 then
                
                
                tlog1=ln_t2(ve(mid)-ve(in)+x,..
                experiment.atom(experiment.jposition).w,experiment.T,experiment.lt);
                tlog2=ln_t2(ve(mid)-ve(in)-x,..
                experiment.atom(experiment.jposition).w,experiment.T,experiment.lt);
                en=fstep_simple((ve(fin)-ve(in)-x)/experiment.T);
                ep=fstep_simple((ve(fin)-ve(in)+x)/experiment.T);
                ytemp=-2*real(rate(mid,fin)*ep.*tlog1);
                ytempn=-2*real(raten(mid,fin)*en.*tlog2);
                
                
                //temporal reverse                
                ytempr=-2*real(rater(mid,fin)*ep.*tlog2);
                ytempnr=-2*real(ratenr(mid,fin)*en.*tlog1);
                
                yp=yp+ytemp;
                yn=yn+ytempn;
                ypr=ypr+ytempr;
                ynr=ynr+ytempnr;
                
              end;
           end; 
          
           z=conv2(-yp(:)-ypr(:),xkernel(:),"same")/1000*(max(x));
           out(fin,in,:)=z(501:1500);
           zn=conv2(-yn($:-1:1)-ynr($:-1:1),xkernel(:),"same")/1000*(max(x));
           outn(fin,in,:)=zn(1500:-1:501);
           //test!!
           //out=-yp(:)-ypr(:);
           //outn=xkernel;
       end;
    end
    close(winH);
endfunction

function [out]=spec3rate_ss(experiment),
    // function to calculate the sample-sample transission probabilities 
    // in 3rd order 
    // experiment has to contain at least the following informations:
    //
    // experiment.T         (temperature)
    // experiment.lt        (lifetime broadening)
    // experiment.ptip      (tip spin-polarizaion)
    // experiment.psample   (sample Spin-polarization)
    // experiment.atom      (either the parameters of an atom or a list of atoms)
    // experiment.Eigenvec  (at least two eigenvectors of the Hamiltonian)
    // experiment.Eigenval  (at least two eigenvalues of the Hamiltonian)
    // experiment.position  (the position of the tip when we have a list of atoms)
    // experiment.jposition (the position where the sample-sample transition takes place)
    //                      (experiment.jposition will be set to experiment.position if not set)
    //
    // additionally, the following global variables have to be set:
    //
    // %precission=0.001    (lower limit of evaluated matrix elements)
    // 
    // 'out' is a matrix with [a,a] elements (a=number of eigenstates)
    // and the following meaning:
    // Rate=out[final-state,initial-state]
    
    txt=getfield(1,experiment);
    if grep(txt,'jposition')==[] then 
        experiment.jposition=experiment.position;
    end;
    ve=experiment.Eigenval;
    if size(ve,1)==size(ve,2) then //if ve is a matrix reduce it to vector
        ve=diag(ve);
    end
    ve=ve-min(real(ve));

    a=size(experiment.Eigenvec,2);
    
    xrange=max([2*ve+20*experiment.T;20*experiment.T]);
    xpoints=floor(max([xrange/experiment.T;1000]));
    x=linspace(-xrange,xrange,xpoints); //integration grid 
    
    f0=fstep_simple(x/experiment.T);
    
    tempexp=experiment;
    tempexp.ptip=tempexp.psample;
    tempexp.atom(:).U=0;
    
    out=zeros(a,a);
    for in=1:a,
        [rate,rater,raten,ratenr]=M35(tempexp,in);
    
        for mid=1:a
            if sum(abs(rate(mid,:))+ abs(rater(mid,:)))>%precission^2 then
                
                tlog1=ln_t2(ve(mid)-ve(in)+x,...
                experiment.atom(experiment.jposition).w,experiment.T,experiment.lt);
                tlog2=tlog1($:-1:1); //reverse the order
                
                for fin=1:a,
                    en=fstep_simple((ve(fin)-ve(in)-x)/experiment.T);

                    ytemp=sum(-2*real(rate(mid,fin)*en'.*tlog2.*f0'));
                    ytempr=sum(-2*real(rater(mid,fin)*en'.*tlog1.*f0'));

                    out(fin,in)=out(fin,in)+(ytemp+ytempr)*2*xrange/(xpoints-1);
                                            
                end
            end
        end
    end
endfunction


////////////////////////////////////////////////////////////////////////////////
//some special graphical functions 
////////////////////////////////////////////////////////////////////////////////

function [bb,w]=Plotstates(S,B),
  // Plot the energy of the eigenstates in dependece of the field B=[0,(Bx, By, Bz)]
  // S must be the spin system with at least
  // S.S as the spin
  // S.g as the gyromagnetic factor
  //
  // if %zeroadj=%T then the lowest state is always at zero energy
  // bb are the energies at field |B|=w

  global %zeroadj;  
  
  b=linspace(0,1,1000);
  bb=b*sqrt(B(1)^2+B(2)^2+B(3)^2);
  clear w;
  
  if %zeroadj==%T then
    for i=1:1000, 
          w(:,i)=spec(HZ(S,b(i)*B)+Haniso(S));
          w(:,i)=w(:,i)-min(w(:,i));
    end;
  else
    for i=1:1000, 
          w(:,i)=spec(HZ(S,b(i)*B)+Haniso(S));
    end;
  end;
  plot(bb',w');
endfunction

function []=blochsphere(rho,varargin)
    // plots the blochsphere of the density matrix rho of a S=1/2 system
    // varagin is the optional color   
    
    //some checks
  drawlater();
  [lhs,rhs]=argn(0); 
  if rhs < 2 then
       col='blue' //default color
  else
       col=varargin(1);
  end
  
  if type(col)==10 then
     col=name2rgb(col);      //col is string
  end

    //check if rho is state-vector or density matrix
    if or(size(rho)==1) then
       rho=rho*rho'; 
    end;

    
    e.S=0.5*(size(rho,2)-1); // determine the spin of the rho
    
    //get the expectation values for Sx,Sy, and Sz.
    //then divide by S so that the values are between -1 and +1.
    
    r=[trace(Sx(e)*rho),trace(Sy(e)*rho),trace(Sz(e)*rho)]/e.S;
    
    if abs(r)==0 then
        r=[0, 0, 0.00001]; //helps to prevent 1/0.
    end
    
    //calculate variables needed for drawing the sphere
    
    gr=100; //gridpoints
    u = linspace(-%pi/2,%pi/2,gr);
    v = linspace(0,2*%pi,gr);
    x= cos(u)'*cos(v);
    xx=cos(v);
    yy=sin(v);
    y= cos(u)'*sin(v);
    z= sin(u)'*ones(v);
    
    param3d1([0;r(1)],[0;r(2)],[0;r(3)])
    
    e=gce()
    e.foreground=color(col(1),col(2),col(3));
    e.thickness=4;
    
    
    //create vector shape
    c1=rand(1,3); //random vector
    temp=find(r<>0); 
    
    temp=temp(1); //reduce to one element
    temp2=find([1 2 3] <> temp) //find the other elements
    c1(temp)=-sum(c1(temp2).*r(temp2))/r(temp);
    c1=c1/sqrt(sum(c1.^2));
    c2=crossp(c1,r)';
    c2=c2/sqrt(sum(c2.^2));
    
    for i=1:20,
        d=2*%pi/20*i;
        vec=r-0.1*r/sqrt(sum(r.^2))+0.05*sin(d)*c1+0.05*cos(d)*c2;
        vecx(2*i)=vec(1);
        vecx(2*i-1)=r(1);
        vecy(2*i)=vec(2);
        vecy(2*i-1)=r(2);
        vecz(2*i)=vec(3);
        vecz(2*i-1)=r(3);
    end
    param3d(vecx,vecy,vecz);
    e=gce();
    e.foreground=color(col(1),col(2),col(3));
    e.thickness=4;
    
    param3d1([-1;1],[0;0],[0;0]);
    e=gce();
    e.line_style=2;
    param3d1([0;0],[-1;1],[-0;0]);
    e=gce();
    e.line_style=2;
    param3d1([0;0],[0;0],[-1;1]);
    e=gce();
    e.line_style=2;
    
    
    //draw the sphere
    plot3d3(xx,yy,zeros(gr,1),theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(zeros(gr,1),xx,yy,theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(xx,zeros(gr,1),yy,theta=100,alpha=70,flag=[6,6,4]);
    h=gcf();
    hh=h.children;
    hh.isoview = "on";
    drawnow();

endfunction


function [ev,vv]=drawstatesphere(rho)
    //this function plots the statesphere of the statevector or density matrix rho
    //it plots an ellipsoid with [<Sx>,<Sy>,<Sz>] as the center and radii
    // <delta Sx>, <delta Sy>, <delta Sz>
    
    
    //check if rho is state-vector or density matrix
    if or(size(rho)==1) then
       rho=rho*rho'; 
    end;
    
    //normalize rho
    l=trace(rho);
    if clean(l)==0 then
        error("Density matrix is not well defined!");
        abort;
    end
    
    rho=rho./l;
    S.S=(size(rho,1)-1)/2; //determine spin
    
    ev(1)=trace(Sx(S)*rho);   //calculate expection values
    ev(2)=trace(Sy(S)*rho);
    ev(3)=trace(Sz(S)*rho);
    
    vv(1)=trace(Sx(S)^2*rho)-ev(1)^2; //calc. variance of evx
    vv(2)=trace(Sy(S)^2*rho)-ev(2)^2;
    vv(3)=trace(Sz(S)^2*rho)-ev(3)^2;
    
    f=gcf();
    drawlater()
    f.color_map = coolcolormap(128);
    //f.color_map = hotcolormap(128);
    r=sqrt(real(vv));orig=real(ev);
    
    deff("[x,y,z]=sph(alp,tet)",["x=r(1)*cos(alp).*cos(tet)+orig(1)*ones(tet)";..
     "y=r(2)*cos(alp).*sin(tet)+orig(2)*ones(tet)";..
     "z=r(3)*sin(alp)+orig(3)*ones(tet)"]);
    [xx,yy,zz]=eval3dp(sph,linspace(-%pi/2,%pi/2,40),linspace(0,%pi*2,20));
    [xx1,yy1,zz1]=eval3dp(sph,linspace(-%pi/2,%pi/2,40),linspace(0,%pi*2,20));
    cc=(xx+zz+2)*32;cc1=(xx1-orig(1)+zz1/max(r)+2)*32;
    plot3d1([xx xx1],[yy yy1],list([zz,zz1],[cc cc1]),theta=70,alpha=80,flag=[5,6,3]);
    
    //plot the sphere
    gr=100; //gridpoints
    r=sqrt(S.S*(S.S+1));
    v = linspace(0,2*%pi,gr);
    xx=r*cos(v);
    yy=r*sin(v);
    
    param3d1([-r;r],[0;0],[0;0]);
    e=gce();
    e.line_style=2;
    param3d1([0;0],[-r;r],[-0;0]);
    e=gce();
    e.line_style=2;
    param3d1([0;0],[0;0],[-r;r]);
    e=gce();
    e.line_style=2;
    
    plot3d3(xx,yy,zeros(gr,1),theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(zeros(gr,1),xx,yy,theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(xx,zeros(gr,1),yy,theta=100,alpha=70,flag=[6,6,4]);
    hh=f.children;
    hh.isoview = "on";
    hh.tight_limits = "on";
    drawnow();
    
endfunction

function []=drawstatehist(rho,varargin)
    //this function plots the distibution of the statevector or density matrix rho
    //The diagonal elements are drawn in red-yellow
    //The conherences (off-diagonal) elements are drawn in blue
    //As varargin 'real' can be given, then only the real part will be drawn
    //As varargin 'scale' can be given, then the scale is [+1,-1];
    
    [lhs,rhs]=argn(0); 
    re=%F;sc=%F
    if rhs > 1 then
        v=varargin();
        re=or(v(1)=='real');
        sc=(v(1)=='scale'|v($)=='scale');
    end
     //check if rho is state-vector or density matrix
    if or(size(rho)==1) then
       rho=rho*rho'; 
    end;
    
    //normalize rho
    l=trace(rho);
    if clean(l)==0 then
        error("Density matrix is not well defined!");
        abort;
    end
    
    rho=rho./l;
    S=(size(rho,1)-1)/2; //determine the spin
    ticks_label=string([S:-1:-S]');
    ticks_label="$|"+ticks_label+"\rangle$";
    ticks_position=[0.5:1:2*S+0.5]';
    ticks=tlist(["ticks","location","labels"],ticks_position, ticks_label);
    
    line=[0:0.2:size(rho,1)];
    line2=[line;line];
    line=0*line+size(rho,1);
    line=[0*line; line];
    
    rhodiag=eye(rho);
    diagmask=ones(rho);
    diagmask(find(rhodiag==0))=%nan;
    coherencemask=ones(rho);
    coherencemask(find(rhodiag==1))=%nan;
    
    drawlater();
    if and (clean(imag(rho))==0) | re then  //if no imag parts are in rho
        hist3d(real(coherencemask.*rho));
        hist3d(real(diagmask.*rho));
    else                                //if imag parts are in rho
        subplot(121);
        hist3d(real(coherencemask.*rho));
        subplot(122);
        hist3d(imag(coherencemask.*rho));
        param3d1(line2,line,0*line);
        param3d1(line,line2,0*line);    
        a=gca();
        a.cube_scaling='on';
        a.x_ticks=ticks;
        a.y_ticks=ticks;
        a.x_label.text="";
        a.y_label.text="";
        a.z_label.text="";
        a.z_label.text="$\Im[\chi]$"
        a.rotation_angles=[70,20];
        if sc then
            a.data_bounds(6)=1;
            a.data_bounds(5)=-1;
        end
        subplot(121);
        hist3d(real(diagmask.*rho));
    end;
    a=gca();
    a.cube_scaling='on';
    a.children(1).hiddencolor=21;
    a.children(1).color_mode=5;
    
    a.x_ticks=ticks;
    a.y_ticks=ticks;
    a.x_label.text="";
    a.y_label.text="";
    a.z_label.text="";
    a.z_label.text="$\Re[\chi]$";
    
    if sc then
        a.data_bounds(6)=1;
        a.data_bounds(5)=-1;
    end
            
    param3d1(line2,line,0*line);
    param3d1(line,line2,0*line);    
    
    a.rotation_angles=[70,20];
    drawnow();
        
endfunction

function drawanisotropy(H,n),
    //this function plots the energy it costs to rotate the density 
    //matrix n into different directions
    //
    //H is the Hamiltonian of the system which contains exactly one spin.
    //We can get H for example by H=Haniso(S)+HZ(S,B) having S.S, S.g, S.D, 
    //S.E, S.DD, and S.G defined. Other creations using the Stevens operators
    //are also possible.
    //Depending on the dimension of n it is either: 
    //The state number in the base system (n is integer)
    //The eigenstate (n is vector)
    //The density matrix (n is matrix)
    
    S.S=(size(H,1)-1)/2; //determine the spin
    
    if size(n)==[1,1] then
        dmz=zeros(H); dmz(n,n)=1; //set the desity matrix
    elseif size(n)==[size(H,1),1] then
        dmz=n*n';
    else
        dmz=n;
    end

    
    tet=linspace(0,2*%pi,40);
    phi=linspace(0,%pi,20);
    
    tet2=ones(length(phi),1).*.tet;
    phi2=phi'.*.ones(1,length(tet));

    x=sin(tet2).*cos(phi2);
    y=sin(tet2).*sin(phi2);
    z=cos(tet2);
    
    e=[];
    for i=1:length(tet),
        for j=1:length(phi),
            rotm=Srot(S,tet(i),[0 1 0]);
            dm=rotm'*dmz*rotm;
            rotm=Srot(S,phi(j),[0 0 1]);
            dm=rotm'*dm*rotm;
            e(j,i)=trace(H*dm);
        end
    end
   
    e=real(e)-min(real(e));
    if and(clean(e)==0) then
        e=e+1;
    end
    x=x.*e;
    y=y.*e;
    z=z.*e;
    
    inda=ones(1,length(phi)-1).*.[0 1 length(phi)+1 length(phi)]+ (1:length(phi)-1).*.[1 1 1 1];
    indb=ones(1,length(phi)-1).*.[1 0 length(phi) length(phi)+1]+ (1:length(phi)-1).*.[1 1 1 1];
    ind2a=ones(1,length(tet)-1).*.inda+((0:length(tet)-2)*length(phi)).*.ones(inda);
    ind2b=ones(1,length(tet)-1).*.indb+((0:length(tet)-2)*length(phi)).*.ones(indb);
    
    ind2=[ind2a(1:length(ind2a)/2),ind2b(length(ind2b)/2+1:$)]
    nx=prod(size(ind2));
    vx=matrix(x(ind2),4,nx/4);
    vy=matrix(y(ind2),4,nx/4);
    vz=matrix(z(ind2),4,nx/4);
    
    cc=real(sqrt(vx.^2+vy.^2+vz.^2));cc=cc/max(cc)*128+0;
    //cc=vx+vz;cc=cc/max(cc)*128+64;
    drawlater();    
    plot3d1([vx],[vy],list([vz],[cc]),theta=70,alpha=80,flag=[5,6,3]);
   
    //plot the sphere
    gr=100; //gridpoints
    r=max(sqrt(x.^2+y.^2+z.^2));//r=0.7
    v = linspace(0,2*%pi,gr);
    xx=r*cos(v);
    yy=r*sin(v);
    
    param3d1([-r;r],[0;0],[0;0]);
    eg=gce();
    eg.line_style=2;
    param3d1([0;0],[-r;r],[-0;0]);
    eg=gce();
    eg.line_style=2;
    param3d1([0;0],[0;0],[-r;r]);
    eg=gce();
    eg.line_style=2;
    
    plot3d3(xx,yy,zeros(gr,1),theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(zeros(gr,1),xx,yy,theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(xx,zeros(gr,1),yy,theta=100,alpha=70,flag=[6,6,4]);
    f=gcf();
    //f.children(1).axes_bounds=[0 0 1 0.6];
    f.children(1).isoview = "on";
    f.children(1).tight_limits = "on";
    f.color_map = jetcolormap(128);
    colorbar(min(e),max(e));
    
    drawnow();
//    title("$\mbox{Visualization of the Magnetic Anisotropy [meV]}$")
    title("$\mbox{Energy of the state vector when pointing in arb. directions}$")



endfunction   

function drawenergy(experiment,n)
    //this function plots the energy it costs to rotate the density 
    //matrix n into different directions.
    //
    //experiment contains all information of the system. In particular:
    //
    //experiment.atom   (either the parameters of an atom or a list of atoms)
    //experiment.B      (the extermal magnetic field)
    //
    //Depending on the dimension of n it is either: 
    //The state number in the base system (n is integer)
    //The eigenstate (n is vector)
    //The density matrix (n is matrix)
    
    //if ~exists('%stopcalc') then
        %stopcalc=%F;
    //end
    
    atomlink=experiment.atom;
    nbr=size(atomlink,2);
    sz=1;
    for i=1:nbr,
            sz=sz*(2*atomlink.S(i)+1);
    end
    
    if size(n)==[1,1] then
        dmz=zeros(sz,sz); dmz(n,n)=1; //set the desity matrix
    elseif size(n)==[sz,1] then
        dmz=n*n';
    else
        dmz=n;
    end
    
    H=hamiltonian(experiment);
    
    tet=linspace(0,2*%pi,40);
    phi=linspace(0,%pi,20);
    
    tet2=ones(length(phi),1).*.tet;
    phi2=phi'.*.ones(1,length(tet));

    x=sin(tet2).*cos(phi2);
    y=sin(tet2).*sin(phi2);
    z=cos(tet2);
    
    e=[];
    winH=waitbar('Calcuating Energies');
    for i=1:length(tet),
        if ~%stopcalc then
            waitbar(i/length(tet),winH);
        else
            close(winH);
            return;
        end;
        for j=1:length(phi),
            rotm=Srotn(atomlink,tet(i),[0 1 0]);
            dm=rotm'*dmz*rotm;
            rotm=Srotn(atomlink,phi(j),[0 0 1]);
            dm=rotm'*dm*rotm;
            e(j,i)=trace(H*dm); 
        end
    end
    close(winH);
   
    e=real(e)-min(real(e));
    if and(clean(e)==0) then
        e=e+1;
    end
    x=x.*e;
    y=y.*e;
    z=z.*e;
    
    inda=ones(1,length(phi)-1).*.[0 1 length(phi)+1 length(phi)]+ (1:length(phi)-1).*.[1 1 1 1];
    indb=ones(1,length(phi)-1).*.[1 0 length(phi) length(phi)+1]+ (1:length(phi)-1).*.[1 1 1 1];
    ind2a=ones(1,length(tet)-1).*.inda+((0:length(tet)-2)*length(phi)).*.ones(inda);
    ind2b=ones(1,length(tet)-1).*.indb+((0:length(tet)-2)*length(phi)).*.ones(indb);
    
    ind2=[ind2a(1:length(ind2a)/2),ind2b(length(ind2b)/2+1:$)]
    nx=prod(size(ind2));
    vx=matrix(x(ind2),4,nx/4);
    vy=matrix(y(ind2),4,nx/4);
    vz=matrix(z(ind2),4,nx/4);
    
    cc=real(sqrt(vx.^2+vy.^2+vz.^2));cc=cc/max(cc)*128+0;
    //cc=vx+vz;cc=cc/max(cc)*128+64;
    drawlater();    
    plot3d1([vx],[vy],list([vz],[cc]),theta=70,alpha=80,flag=[5,6,3]);
   
    //plot the sphere
    gr=100; //gridpoints
    r=max(sqrt(x.^2+y.^2+z.^2));
    v = linspace(0,2*%pi,gr);
    xx=r*cos(v);
    yy=r*sin(v);
    
    param3d1([-r;r],[0;0],[0;0]);
    eg=gce();
    eg.line_style=2;
    param3d1([0;0],[-r;r],[-0;0]);
    eg=gce();
    eg.line_style=2;
    param3d1([0;0],[0;0],[-r;r]);
    eg=gce();
    eg.line_style=2;
    
    plot3d3(xx,yy,zeros(gr,1),theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(zeros(gr,1),xx,yy,theta=70,alpha=80,flag=[6,6,3]);
    plot3d3(xx,zeros(gr,1),yy,theta=100,alpha=70,flag=[6,6,4]);
    f=gcf();
    //f.children(1).axes_bounds=[0 0 1 0.6];
    f.children(1).isoview = "on";
    f.children(1).tight_limits = "on";
    f.color_map = jetcolormap(128);
    colorbar(min(e),max(e));
    
    drawnow();
//    title("$\mbox{Visualization of the Magnetic Anisotropy [meV]}$")
    title("$\mbox{Energy of the state vector when pointing in arb. directions}$")

endfunction   

function [dm]=densitymatrix(experiment),
    
    [a,b]=size(experiment.Eigenvec);
    occ=Occupation(experiment.Eigenval,experiment.T);
    dm=[];
    for i=1:b,
        //v=sparse(clean(experiment.Eigenvec(:,i)));
        //dm=dm+occ(i)*(v*v');
        dm=dm+occ(i)*(experiment.Eigenvec(:,i)*experiment.Eigenvec(:,i)')
    end
    
endfunction

////////////////////////////////////////////////////////////////////////////////
//some QC functions
////////////////////////////////////////////////////////////////////////////////

funcprot(1);
