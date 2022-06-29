////////////////////////////////////////////////////////////////////////////////
//
//    Spin Hamiltonains 1.0.sce
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
// Basic spin operators
////////////////////////////////////////////////////////////////////////////////

function [e]=Splus(S),
  //prepare the S+ matrix
  //S.S must be the spin of the system
  e = sqrt((1:2*S.S).*(2*S.S:-1:1));
  e=diag(e,+1);
endfunction

function [e]=Sminus(S),
  //prepare the S- matrix
  //S.S must be the spin of the system
  e = sqrt((1:2*S.S).*(2*S.S:-1:1));
  e=diag(e,-1);
endfunction

function [e]=Sx(S),
  //prepare the Sx matrix
  //S.S must be the spin of the system
  e=0.5*(Splus(S)+Sminus(S));
endfunction

function [e]=Sy(S),
  //prepare the Sy matrix
  //S.S must be the spin of the system
  e=-0.5*%i*(Splus(S)-Sminus(S));
endfunction

function [e]=Sz(S),
  //prepare the Sz matrix with diagonal elements -S, -S+1,...,+S
  //S.S must be the spin of the system
  e=diag([S.S:-1:-S.S]);
endfunction

function [e]=Sarb(S,varargin),
  //prepare a S matrix with arbitary directions
  //S.S must be the spin of the system
  //varargin must contain either the rotation angles theta and phi
  //or the direction (x,y,z)
  [lhs,rhs]=argn(0);
  if rhs > 3 then
       x=varargin(1);
       y=varargin(2);
       z=varargin(3);
       theta=acos(z/sqrt(x^2+y^2+z^2));
       if isnan(theta) then
           theta=0;
       end
       phi=atan(y,x);
  else
       theta=varargin(1);
       phi=varargin(2);
  end
  e=expm(-%i*Sy(S)*theta)*Sz(S)*expm(%i*Sy(S)*theta); //rotate around y
  e=expm(-%i*Sz(S)*phi)*e*expm(%i*Sz(S)*phi);         //rotate around z
endfunction

function [e]=S1(S)
    //prepare the unity matrix for system S
    //S.S must be the spin of the system
    e=diag(ones(S.S*2+1,1));
endfunction
    
function [e]=S2(S),
 //prepare the S^2 matrix
 //S.S must be the spin of the system
  e=Sx(S)*Sx(S)+Sy(S)*Sy(S)+Sz(S)*Sz(S);
endfunction

function [e]=Srot(S,phi,n),
  // prepare the rotational matrix 
  // of the spin system S 
  // rotation angle phi
  // rotational axis n (must have length 1)
  e=clean(expm(-%i*phi*(Sx(S)*n(1)+Sy(S)*n(2)+Sz(S)*n(3))));
endfunction

function [e]=dmatrix(n)
    // create the Density Matrix for spin 1/2 electrons which have a polarization
    // in the direction n and a polarization strength -1<|n|<1.
    S.S=1/2;
    e=(1/2*S1(S)+n(1)*Sx(S)+n(2)*Sy(S)+n(3)*Sz(S));
endfunction

////////////////////////////////////////////////////////////////////////////////
// Basic spin operators for spin ensembles
////////////////////////////////////////////////////////////////////////////////

function [e]=Sxn(t),
  //prepare the Sx matrix for an ensemble t of spins
  //Szn([Fe,Co,...])
  b=size(t,2);     // determine the number of coupled spins

  e=[];
  for i=1:b,
      x=1;
      for j=1:i-1, 
          x=x.*.sparse(S1(t(j))); 
      end;
      x=x.*.sparse(Sx(t(i)));
     for j=i+1:b, 
          x=x.*.sparse(S1(t(j)));
     end;
     e=e+x;
  end;
endfunction

function [e]=Syn(t),
  //prepare the Sy matrix for an ensemble t of spins
  //Szn([Fe,Co,...])
  b=size(t,2);     // determine the number of coupled spins

  e=[];
  for i=1:b,
      x=1;
      for j=1:i-1, 
          x=x.*.sparse(S1(t(j))); 
      end;
      x=x.*.sparse(Sy(t(i)));
     for j=i+1:b, 
          x=x.*.sparse(S1(t(j)));
     end;
     e=e+x;
  end;
endfunction

function [e]=Szn(t),
  //prepare the Sz matrix for an ensemble t of spins
  //Szn([Fe,Co,...])
  b=size(t,2);     // determine the number of coupled spins

  e=[];
  for i=1:b,
      x=1;
      for j=1:i-1, 
          x=x.*.sparse(S1(t(j))); 
      end;
      x=x.*.sparse(Sz(t(i)));
     for j=i+1:b, 
          x=x.*.sparse(S1(t(j)));
     end;
     e=e+x;
  end;
endfunction

function [e]=Sarbn(t,varargin),
  //prepare a S matrix with arbitary directions
  //for an ensemble t of spins
  //varargin must contain either the rotation angles theta and phi
  //or the direction (x,y,z)
  //Sarbn([Fe,Co,...],x,y,z)
  b=size(t,2);     // determine the number of coupled spins
  
  [lhs,rhs]=argn(0);
  if rhs > 3 then
       x=varargin(1);
       y=varargin(2);
       z=varargin(3);
       theta=acos(z/sqrt(x^2+y^2+z^2));
       if isnan(theta) then
           theta=0;
       end;
       phi=atan(y,x);
  else
       theta=varargin(1);
       phi=varargin(2);
  end
 
  e=[];
  for i=1:b,
      x=1;
      for j=1:i-1, 
          x=x.*.sparse(S1(t(j))); 
      end;
      y=expm(-%i*Sy(t(i))*theta)*Sz(t(i))*expm(%i*Sy(t(i))*theta); //rotate around y
      y=clean(expm(-%i*Sz(t(i))*phi)*y*expm(%i*Sz(t(i))*phi));      //rotate around z
      x=x.*.sparse(y);
     for j=i+1:b, 
          x=x.*.sparse(S1(t(j)));
     end;
     e=e+x;
  end;
endfunction

function [e]=S2n(t),
  //prepare the S^2 matrix for an ensemble t of spins
  //S2n([Fe,Co,...])
  e=Sxn(t)^2+Syn(t)^2+Szn(t)^2;
endfunction

function [e]=Srotn(S,phi,n),
  // prepare the rotational matrix 
  // of the spin system S 
  // rotation angle phi
  // rotational axis n (must have length 1)

  e=clean(expm(full(-%i*phi*(Sxn(S)*n(1)+Syn(S)*n(2)+Szn(S)*n(3)))));      

endfunction

////////////////////////////////////////////////////////////////////////////////
// Basic Energy Hamiltonians
////////////////////////////////////////////////////////////////////////////////

function [e]=HZ(S,B),
    //prepare Zeemann Hamiltonian HZ
    //S is the spin system with at least
    //S.S as the spin
    //S.g as the gyomagnetic factor
    //B is the external field 
    a=sum(size(B)); //check if B is 1dim or 3dim
    if a<>2 & a<>4 then error(5);abort;
    end;
    if a==2 then B=[0,0,B]; //assign B to B_Z if B is 1dim
    end;
    e=S.g*0.05788*(B(1)*Sx(S)+B(2)*Sy(S)+B(3)*Sz(S))
endfunction

function [e]=Haniso(S),
    //prepare the anisotropy Hamiltonian
    //S is the spin system with at least
    //S.S as the spin
    //S.D, S.E, S.DD, and S.G will be used for the calculation if they exist
    txt=getfield(1,S);
    //check what parameters we have
    if grep(txt,'D')==[] then S.D=0, end;
    if grep(txt,'E')==[] then S.E=0, end;
    e=S.D*(Sz(S)*Sz(S))+S.E*(Sx(S)*Sx(S)-Sy(S)*Sy(S)),
    if grep(txt,'DD') then 
        e=e+S.DD*(Sz(S)^4),
    end;
    if grep(txt,'G') then 
        e=e+S.G*(Splus(S)^4+Sminus(S)^4),
    end;
endfunction

function [e]=HHeisenberg(t,J,n,m),
    //Create a Hamiltonian which couple two spins (n and m) 
    //from an ensemble t of spins with the Heisenberg interaction J.
    //HHeisenberg([Fe,Co,...],J,n,m)
    
    a=sum(size(J)); //check if J is 1dim or 3dim
    if a<>2 & a<>4 then error(5);abort;
    end;
    if a==2 then J=[J,J,J]; //if J is 1dim assign Jx=J,Jy=J,Jz=J
    end;

    b=size(t,2)     // determine the number of coupled spins
    //make some checks!
    if (b<n) | (b<m) | (n==m) then error(1);abort;
    end
    if n>m then p=n;n=m;m=p; //swap n and m
    end

    x=1;y=1;z=1;
    for j=1:n-1, 
        m1=sparse(S1(t(j)));
        x=x.*.m1; 
        y=y.*.m1; 
        z=z.*.m1; 
    end;
    x=x.*.sparse(Sx(t(n)));
    y=y.*.sparse(Sy(t(n)));
    z=z.*.sparse(Sz(t(n)));
    for j=n+1:m-1, 
        m1=sparse(S1(t(j)));
        x=x.*.m1; 
        y=y.*.m1; 
        z=z.*.m1; 
    end;
    x=x.*.sparse(Sx(t(m)));
    y=y.*.sparse(Sy(t(m)));
    z=z.*.sparse(Sz(t(m)));
    for j=m+1:b, 
        m1=sparse(S1(t(j)));
        x=x.*.m1; 
        y=y.*.m1; 
        z=z.*.m1; 
    end;

    e=J(1)*x+J(2)*y+J(3)*z;
endfunction

function [e]=HDM(t,D,n,m),
    //Create a Hamiltonian which couples two spins (n and m) 
    //from an ensemble t of spins with the DM interaction D.
    //HDM([Fe,Co,...],D,n,m) 
     
    b=size(t,2);     // determine the number of coupled spins
    //make some checks!
    if (b<n) | (b<m) | (n==m) then error(1);abort;
    end
    if n>m then p=n;n=m;m=p;D=-D; //swap n and m and change sign of D
    end
    
    x=1;y=1;z=1;xx=1;yy=1;zz=1;
    
    for j=1:n-1, 
        x=x.*.sparse(S1(t(j)));
        xx=x;y=x;yy=x;z=x;zz=x;
    end;
    x=x.*.sparse(Sy(t(n)));xx=xx.*.sparse(Sz(t(n)));
    y=y.*.sparse(Sz(t(n)));yy=yy.*.sparse(Sx(t(n)));
    z=z.*.sparse(Sx(t(n)));zz=zz.*.sparse(Sy(t(n)));
    for j=n+1:m-1, 
        m1=sparse(S1(t(j)));
        x=x.*.m1;xx=xx.*.m1; 
        y=y.*.m1;yy=yy.*.m1; 
        z=z.*.m1;zz=zz.*.m1;  
    end;
    x=x.*.sparse(Sz(t(m)));xx=xx.*.sparse(Sy(t(m)));
    y=y.*.sparse(Sx(t(m)));yy=yy.*.sparse(Sz(t(m)));
    z=z.*.sparse(Sy(t(m)));zz=zz.*.sparse(Sx(t(m)));
    for j=m+1:b, 
        m1=sparse(S1(t(j)));
        x=x.*.m1;xx=xx.*.m1; 
        y=y.*.m1;yy=yy.*.m1; 
        z=z.*.m1;zz=zz.*.m1;  
    end;
    e=D(1)*(x-xx)+D(2)*(y-yy)+D(3)*(z-zz);
endfunction

function [e]=HAni(t,B),
    //Create a Hamiltonian in which all spins of the ensemble t
    //have their anisotropy and Zeeman energy included
    //HAni([Fe,Co,...],B)  
    b=size(t,2)     // determine the number of coupled spins
    if b==1  then   //only one atom
        e=Haniso(t)+HZ(t,B);
    else
        e=[];
        for i=1:b,
            x=1
            for j=1:i-1, 
                x=x.*.sparse(S1(t(j))); 
            end;
            x=x.*.sparse(Haniso(t(i))+HZ(t(i),B))
            for j=i+1:b, 
                x=x.*.sparse(S1(t(j)));
            end;
            e=e+x;
        end;    
    end
endfunction

function H=hamiltonian(experiment),
    //This function calculates the total Hamiltonian of a coupled spin system
    //
    // experiment has to contain at least the following information:
    //
    // experiment.atom                  (either the parameters of an atom or a list of atoms)
    // experiment.B                     (the external field)
    //
    // furthermore, the following additional parameters are possible
    // experiment.heisenberg_coupling   (the global coupling constant)
    // experiment.matrix                (the Heisenberg coupling constant between the (i,i+1)th atom)
    // experiment.matrixDM              (the DM coupling vector between the (i,i+1)th atom)
    //build the Zeeman and Anisotropy Hamiltonian
     
    H=HAni(experiment.atom,experiment.B);
    
    if size(experiment.atom,2)>1  then
        
        //check if we have Heisenberg coupling
        if or(getfield(1,experiment)=='matrix') then
            M=experiment.matrix;
            J=experiment.heisenberg_coupling;
            if J<>0 then
                for i=1:size(M,1),
                    for j=2:size(M,2)+1,
                        if j>i then
                            H=H+HHeisenberg(experiment.atom,evstr(M(i,j-1))*J,i,j);
                        end
                    end
                end
            end
        end
        
        //check if we have DM coupling
        if or(getfield(1,experiment)=='matrixDM') then
            M=experiment.matrixDM;
            J=experiment.heisenberg_coupling;
            if J<>0 then
                for i=1:size(M,1),
                    for j=2:size(M,2)+1,
                        if j>i then
                            H=H+HDM(experiment.atom,evstr(M(i,j-1))*J,i,j);
                        end
                    end
                end
            end
        end
   end
   
endfunction

function eigenvalues(experiment),
    //the function calculates the eigenvectors and eigenvalues
    //and stores them in experiment.Eigenvec and experiment.Eigenval
    //
    // experiment has to contain at least the following information:
    //
    // experiment.atom                  (either the parameters of an atom or a list of atoms)
    // experiment.B                     (the external field)
    // experiment.max_no_eigenstates    (the maximal number of calculated eigenvectors)
    //
    // furthermore, the following additional parameters are possible
    // experiment.heisenberg_coupling   (the global coupling constant)
    // experiment.matrix                (the Heisenberg coupling constant between the (i,i+1)th atom)
    // experiment.matrixDM              (the DM coupling vector between the (i,i+1)th atom)
    
    
    global experiment;
    
    H=hamiltonian(experiment);
       // solve the eigenvalue-problem
    if or(getfield(1,experiment)=='max_no_eigenstates') then //check if max_no_eigenstates exist
        if size(H,1) < experiment.max_no_eigenstates+2 then
            [experiment.Eigenvec,experiment.Eigenval]=spec(full(H));
        else
            ofst=0;ofstold=0;
            while ofst >= 0
                H=H-ofst*speye(H); /////
                [experiment.Eigenval,experiment.Eigenvec]=eigs(H,speye(H),experiment.max_no_eigenstates);
                ofstold=ofstold+ofst;
                ofst=max(real(diag(experiment.Eigenval)));
            end
            if ofstold > 0 then
               experiment.Eigenval=experiment.Eigenval+ofstold*eye(experiment.Eigenval);
            end
        end
    else
        [experiment.Eigenvec,experiment.Eigenval]=spec(full(H));
    end
    experiment.Eigenval=diag(real(experiment.Eigenval));
    experiment.Eigenvec=clean(experiment.Eigenvec);

endfunction

////////////////////////////////////////////////////////////////////////////////
// Additional Hamiltonians and matrix functions for special purposes
////////////////////////////////////////////////////////////////////////////////

function [e]=traceout(rho,t,n);
   
   // fuction to traceout parts of the full density matrix
   //    
   // rho is the density matrix of the full system
   // t is a struct array of the corresponding coupled atoms
   // n is a vector containing the number of spins in the spin list 
   // of the reduced density matrix
   // n must be a contious list i.e. [2,3,4] but NOT [2,4,5]!
   // e is finaly the reduced density matrix
   // ATTENTION! The list n contains the remaining atoms in the new density matrix
   
    n=gsort(n,'g','i');
    b=size(t,2);     // determine the number of coupled spins
    c0=1;
    for i=n,
        c0=c0*(2*t(i).S+1);
    end
    c0=zeros(c0,c0);
    e=zeros(c0);
    for i=1:length(e),
        x=1;
        for j=1:min(n)-1, 
            x=x.*.sparse(S1(t(j))); 
        end;
        c=c0; 
        c(i)=1;
        x=x.*.c;
        for j=max(n)+1:b, 
            x=x.*.sparse(S1(t(j)));
        end;
        e(i)=sum(x.*rho);
    end;
endfunction

function [e]=ptranspose(rho,t,n);
   
   // Function to partly transpose a density matrix
   // 
   // rho is the (density) matrix of the full system
   // t is a struct array of the corresponding coupled atoms
   // n is a vector containing the number of spins which shall be transposed 
   // e is finaly partially transposed (density) matrix
   
    
    zout=size(rho,2);
    b=size(t,2);     // determine the number of coupled spins
    
    for i=1:b,
        sz(i)=2*t.S(i)+1; 
    end
    
    p=[1:2*b];
    p([b+1-n,2*b+1-n]) = p([2*b+1-n,b+1-n]);
    
    e=matrix(permute(matrix(rho,[sz($:-1:1),sz($:-1:1)]),p),zout,zout);
   
endfunction
function [e]=permuterho(rho,t,n);
   
   // function to permute the submatrices of the total density matrix
    
   // rho is the (density) matrix or a state vector of the system
   // t is a struct array of the corresponding coupled atoms
   // n is a vector containing the new order of spins 
   // e is finaly the permuted (density) matrix
   
    
    zout=size(rho); //determine the size of the input
    b=size(t,2);     // determine the number of coupled spins
    
    for i=1:b,
        sz(i)=2*t.S(i)+1; //detemine the sizes of the subsystems
    end
    
    if or(zout==1) then  //state vector
        p = b+1-n($:-1:1);
        e=matrix(permute(matrix(rho,sz($:-1:1)),p),zout);
    else
         p = b+1-n($:-1:1);
         p = [p,b+p];
          e=matrix(permute(matrix(rho,[sz($:-1:1),sz($:-1:1)]),p),zout);
       
    end
   
endfunction

////////////////////////////////////////////////////////////////////////////////
// Calculations of Transition Matrix elements
////////////////////////////////////////////////////////////////////////////////

function [x,y,z,u]=etransport(experiment),
// this function calculates the transition matrix elements for the tunneling and
// interacting S=1/2 electrons in their spin base. Thus, it gives the transport 
// probabilities for arbitrary polarized electrons in tip and sample.
// experiment.ptip and experiment.psample must be the 3dim spin polarization of
// tip and sample, respectively.
// 'plus' the matrix <f|sigma+|i>
// 'minus' the matrix <f|sigma-|i>
// 'z' the matrix <f|sigma_z|i>
// 'U' the matrix <f|i> 
   
  e.S=1/2;
  dt=dmatrix(experiment.ptip);
  ds=dmatrix(experiment.psample);
  [wt,pt]=spec(dt);
  [ws,ps]=spec(ds);

  pt=diag(pt);
  ps=diag(ps);

  pp=sqrt(ps.*.pt');  
  
  //the factor 2 originates from the differences between Pauli-matices and S matrices
  x=(ws'*(2*Sx(e))*wt).*pp;
  y=(ws'*(2*Sy(e))*wt).*pp;
  z=(ws'*(2*Sz(e))*wt).*pp;
  u=-2*(ws'*wt).*pp;
      
endfunction

function [e, er, en, enr]=e_epsilon(experiment),
    // calculate the tunneling rate in 3rd order
    // via all possible tunneling pathes FOR THE ELECTRONS
    // output are 4 tensors (size 4x4x4) which give the probabiliy to tunnel from i->j->k
    // e is the 'normal' tensor for tunneling from tip to sample
    // er is the 'time-reversed' tensor for tunneling from tip to sample     
    // en is the 'normal' tensor for tunneling from sample to tip
    // enr is the 'time-reversed' tensor for tunneling from sample to tip
    // experiment has to contain:
    // 'experiment.ptip':     spin polarization of the tip
    // 'experiment.psample':  spin polarization of the sample
   
    [x,y,z,u]=etransport(experiment);
    
    tempexperiment=experiment;
    tempexperiment.ptip=tempexperiment.psample;
    [xs,ys,zs,us]=etransport(tempexperiment);
    
    mone=ones(1,2);   
    so1=list(x, y, z, u);
    so2=list(xs, ys, zs, us);
    so3=list(x', y', z', u');
    e=zeros(4,4,4);er=e;en=e;enr=e;
    for j=1:4,
       for k=1:4,
          for l=1:4,
             for in=1:2,          
                 temp=(mone'.*.so3(l)(in,:)).*(so2(k)).'.*(mone.*.so1(j)(:,in));    
                e(j,k,l)=e(j,k,l)+sum(temp);
                
                 temp=-(mone'.*.so3(l)(in,:)).*(mone.*.so1(k)(:,in)).*(so2(j).');
                er(j,k,l)=er(j,k,l)+sum(temp);
                
                 temp=-(mone.*.so1(l)(:,in)).*(so2(k)).'.*(mone'.*.so3(j)(in,:));
                en(j,k,l)=en(j,k,l)+sum(temp);
                
                 temp=(mone.*.so1(l)(:,in)).*(mone'.*.so3(k)(in,:)).*(so2(j).');
                enr(j,k,l)=enr(j,k,l)+sum(temp);
             end;
          end;
       end;
    end;
endfunction

function [out1,out2,out3,out4]=Rate2nd(experiment),
  // calculate the tunneling matrix elements up to 2nd order
  // via all possible tunneling pathes
  // i.e.
  // out1= <f,u'|Sx+Sy+Sz+U|i,u>
  // out2= <f,u'|Sx+Sy+Sz+U|i,d>
  // out3= <f,d'|Sx+Sy+Sz+U|i,u>
  // out4= <f,d'|Sx+Sy+Sz+U|i,d>
  // with u/d and u'/d' as the two eigenstates in tip and sample, respectively.
  // experiment has to contain:
  // 'experiment.ptip':     spin polarization of the tip
  // 'experiment.psample':  spin polarization of the sample
  // 'experiment.Eigenvec': matrix of the eigenvectors of the spin ensemble
  // 'experiment.atom':     a list with the atoms of the system 
  // 'experiment.position': position in the atom list at which the rate is calc.
  
  //first we calculate the transition matrices for the tunneling electron
  [x,y,z,u]=etransport(experiment);

  E=experiment.Eigenvec;
  if ~isvector(experiment.atom) then
      // go the easy way! It's only one spin-system
      S=experiment.atom;

      matrxx=Sx(S);
      matrxy=Sy(S);
      matrxz=Sz(S);
      matrxu=S.U*S1(S);
      
  else
      nr=experiment.position;
      natoms=size(experiment.atom);
      matrxx=1;

      for i=1:(nr-1),
          mm=sparse(S1(experiment.atom(i)));
          matrxx=matrxx.*.mm;
      end
      matrxy=matrxx;
      matrxz=matrxx;
      matrxu=matrxx;
      S=experiment.atom(nr);
      matrxx=matrxx.*.Sx(S);
      matrxy=matrxy.*.Sy(S);
      matrxz=matrxz.*.Sz(S);
      matrxu=matrxu*S.U.*.S1(S);

      for i=nr+1:natoms(2),
          mm=sparse(S1(experiment.atom(i)));
          matrxx=matrxx.*.mm;
          matrxy=matrxy.*.mm;
          matrxz=matrxz.*.mm;
          matrxu=matrxu.*.mm;                              
      end
  end
  matrxx=E'*matrxx*E;
  matrxy=E'*matrxy*E;
  matrxz=E'*matrxz*E;
  matrxu=E'*matrxu*E;

      out1=(matrxx*x(1)+matrxy*y(1)+matrxz*z(1)+matrxu*u(1));
      out2=(matrxx*x(2)+matrxy*y(2)+matrxz*z(2)+matrxu*u(2));
      out3=(matrxx*x(3)+matrxy*y(3)+matrxz*z(3)+matrxu*u(3));
      out4=(matrxx*x(4)+matrxy*y(4)+matrxz*z(4)+matrxu*u(4));
      
endfunction

function [out]=Rate2nd2(experiment),
  // calculate the tunneling rate up to 2nd order
  // via all possible tunneling pathes
  // i.e.
  // <f|Sx+Sy+Sz+U|i>^2
  // 'out' is a matrix which gives the probabiliy to tunnel from i->j
  // experiment has to contain:
  // 'experiment.ptip':     spin polarization of the tip
  // 'experiment.psample':  spin polarization of the sample
  // 'experiment.Eigenvec': matrix of the eigenvectors of the spin ensemble
  // 'experiment.atom':     a list with the atoms of the system 
  // 'experiment.position': position in the atom list at which the rate is calc.
  
  //first we calculate the transition matrices for the tunneling electron
  [x,y,z,u]=etransport(experiment);

  E=experiment.Eigenvec;
  if ~isvector(experiment.atom) then
      // go the easy way! It's only one spin-system
      S=experiment.atom;

      matrxx=Sx(S);
      matrxy=Sy(S);
      matrxz=Sz(S);
      matrxu=S.U*S1(S);
      
  else
      nr=experiment.position;
      natoms=size(experiment.atom);
      matrxx=1;

      for i=1:(nr-1),
          mm=sparse(S1(experiment.atom(i)));
          matrxx=matrxx.*.mm;
      end
      matrxy=matrxx;
      matrxz=matrxx;
      matrxu=matrxx;
      S=experiment.atom(nr);
      matrxx=matrxx.*.Sx(S);
      matrxy=matrxy.*.Sy(S);
      matrxz=matrxz.*.Sz(S);
      matrxu=matrxu*S.U.*.S1(S);

      for i=nr+1:natoms(2),
          mm=sparse(S1(experiment.atom(i)));
          matrxx=matrxx.*.mm;
          matrxy=matrxy.*.mm;
          matrxz=matrxz.*.mm;
          matrxu=matrxu.*.mm;                              
      end
  end
  matrxx=E'*matrxx*E;
  matrxy=E'*matrxy*E;
  matrxz=E'*matrxz*E;
  matrxu=E'*matrxu*E;

  out=[];
  for i=1:4,
      out=out+abs(matrxx*x(i)+matrxy*y(i)+matrxz*z(i)+matrxu*u(i)).^2;
  end

endfunction

function [e,er,en,enr]=M35(experiment,in),
    // calculate the tunneling rate in 3rd order
    // via all possible tunneling pathes
    // output are 4 matrices which give the probabiliy to tunnel from in->i->j
    // e is the 'normal' matrix for tunneling from tip to sample
    // er is the 'time-reversed' matrix for tunneling from tip to sample     
    // en is the 'normal' matrix for tunneling from sample to tip
    // enr is the 'time-reversed' matrix for tunneling from sample to tip
    // experiment has to contain:
    // 'experiment.ptip':     spin polarization of the tip
    // 'experiment.psample':  spin polarization of the sample
    // 'experiment.Eigenvec': matrix of the eigenvectors of the spin ensemble
    // 'experiment.atom':     a list containing the atoms of the system 
    // 'experiment.position': is the number of the atom in the ensemble with 
    //                        which the tunneling electron interacts
    // 'experiment.jposition':is the number of the atom in the ensemble with
    //                        which the sample-to-sample electron interacts
    // 'in' is the number of the initial state

    //first we calculate the transition matrices for the electrons in 3rd order
    
   E=experiment.Eigenvec; a=size(E);
    
   [e_sig, er_sig, en_sig, enr_sig]=e_epsilon(experiment);    
          
   if ~isvector(experiment.atom) then
      // go the easy way! It's only one spin-system
      S=experiment.atom;
    
      matrxx=E'*Sx(S)*E;
      matrxy=E'*Sy(S)*E;
      matrxz=E'*Sz(S)*E;
      matrxu=S.U*E'*S1(S)*E;
      
      if length(S.J) == 1 then
          J(1)=S.J;J(2)=S.J;J(3)=S.J;
      else
          J=S.J;
      end
      
      Smatrxx=J(1)*matrxx;
      Smatrxy=J(2)*matrxy;
      Smatrxz=J(3)*matrxz;
      Smatrxu=zeros(Smatrxx);

else
    txt=getfield(1,experiment);
    if grep(txt,'entanglement')==[] then
        experiment.entanglement=%F; //standart is no entanglement
    end;

      nr=experiment.position;
      nrj=experiment.jposition;
      natoms=size(experiment.atom);
      matrxx=1;
      for i=1:(nr-1),
          matrxx=matrxx.*.sparse(S1(experiment.atom(i)));
      end
      
      matrxy=matrxx;
      matrxz=matrxx;
      matrxu=matrxx;
      
      matrxx=matrxx.*.sparse(Sx(experiment.atom(nr)));
      matrxy=matrxy.*.sparse(Sy(experiment.atom(nr)));
      matrxz=matrxz.*.sparse(Sz(experiment.atom(nr)));
      matrxu=experiment.atom(nr).U*matrxu.*.sparse(S1(experiment.atom(nr)));
      
      for i=nr+1:natoms(2),
          tempm=sparse(S1(experiment.atom(i)));
          matrxx=matrxx.*.tempm;
          matrxy=matrxy.*.tempm;
          matrxz=matrxz.*.tempm;
          matrxu=matrxu.*.tempm;
      end
      if nrj==nr & ~experiment.entanglement then    //no entanglement
          
          J=experiment.atom(nrj).J;
          if length(J) == 1 then
              JT=J;
              J(1)=JT;J(2)=JT;J(3)=JT;
          end

          Smatrxx=J(1)*E'*matrxx*E;
          Smatrxy=J(2)*E'*matrxy*E;
          Smatrxz=J(3)*E'*matrxz*E;
          Smatrxu=spzeros(Smatrxx);
          
      elseif ~experiment.entanglement then          //no entanglement
          Smatrxx=1;                                //and nrj<>nr
          
          for i=1:(nrj-1),
              Smatrxx=Smatrxx.*.sparse(S1(experiment.atom(i)));
          end
          
          Smatrxy=Smatrxx;
          Smatrxz=Smatrxx;
          
          Smatrxx=Smatrxx.*.sparse(Sx(experiment.atom(nrj)));
          Smatrxy=Smatrxy.*.sparse(Sy(experiment.atom(nrj)));
          Smatrxz=Smatrxz.*.sparse(Sz(experiment.atom(nrj)));
          for i=nrj+1:natoms(2),
              tempm=sparse(S1(experiment.atom(i)))
              Smatrxx=Smatrxx.*.tempm;
              Smatrxy=Smatrxy.*.tempm;
              Smatrxz=Smatrxz.*.tempm;
          end
          J=experiment.atom(nrj).J;
          if length(J) == 1 then
              JT=J;
              J(1)=JT;J(2)=JT;J(3)=JT;
          end

          Smatrxx=J(1)*E'*Smatrxx*E;
          Smatrxy=J(2)*E'*Smatrxy*E;
          Smatrxz=J(3)*E'*Smatrxz*E;
          Smatrxu=spzeros(Smatrxx);
          
      else      //entaglement
          Smatrxx=[];
          Smatrxy=[];
          Smatrxz=[];
          
          for j=1:natoms(2),
              Stmatrxx=1;                                
          
              for i=1:(j-1),
                  Stmatrxx=Stmatrxx.*.sparse(S1(experiment.atom(i)));
              end
              
              Stmatrxy=Stmatrxx;
              Stmatrxz=Stmatrxx;
          
              Stmatrxx=Stmatrxx.*.sparse(Sx(experiment.atom(j)));
              Stmatrxy=Stmatrxy.*.sparse(Sy(experiment.atom(j)));
              Stmatrxz=Stmatrxz.*.sparse(Sz(experiment.atom(j)));
              for i=j+1:natoms(2),
                tempm=sparse(S1(experiment.atom(i)))
                Stmatrxx=Stmatrxx.*.tempm;
                Stmatrxy=Stmatrxy.*.tempm;
                Stmatrxz=Stmatrxz.*.tempm;
              end
              J=experiment.atom(j).J;
              if length(J) == 1 then
                JT=J;
                J(1)=JT;J(2)=JT;J(3)=JT;
              end

              Smatrxx=Smatrxx+J(1)*E'*Stmatrxx*E;
              Smatrxy=Smatrxy+J(2)*E'*Stmatrxy*E;
              Smatrxz=Smatrxz+J(3)*E'*Stmatrxz*E;
          end
          Smatrxu=spzeros(Smatrxx);
      end      
   
      matrxx=E'*matrxx*E;
      matrxy=E'*matrxy*E;
      matrxz=E'*matrxz*E;
      matrxu=E'*matrxu*E;
      
    
  end
    
    mone=ones(1,a(2));     
            
    so1=list(matrxx,matrxy,matrxz,matrxu);
    so2=list(Smatrxx,Smatrxy,Smatrxz,Smatrxu);
    so3=so1;
    e=[];er=[];en=[];enr=[];
    for j=1:4,
        for k=1:4,
            for l=1:4,
                  if  e_sig(j,k,l)<>0 then
                      e=e-e_sig(j,k,l)*(mone'.*.so3(l)(in,:)).*(so2(k)).'.*(mone.*.so1(j)(:,in));
                  end
                  if er_sig(j,k,l)<>0 then
                      er=er-er_sig(j,k,l)*(mone'.*.so3(l)(in,:)).*(so1(k)).'.*(mone.*.so2(j)(:,in));
                  end
                  if en_sig(j,k,l)<>0 then
                      en=en-en_sig(j,k,l)*(mone'.*.so1(l)(in,:)).*(so2(k)).'.*(mone.*.so3(j)(:,in));    
                  end
                  if enr_sig(j,k,l)<>0 then
                      enr=enr-enr_sig(j,k,l)*(mone'.*.so1(l)(in,:)).*(so3(k)).'.*(mone.*.so2(j)(:,in));
                  end
            end
        end
   end
   
   e=clean(e);
   er=clean(er);
   en=clean(en);
   enr=clean(enr);
   
endfunction
