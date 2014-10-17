#include "Riostream.h"
#include <iostream>
#include "TString.h"
#include "TMath.h"
#include "TGraph.h"
#include <vector>


gROOT->Reset();
gROOT->SetStyle("Plain");



//define lorentz function (fixed function for 0° and 90°)
//provides FWHM
Double_t FitFuncLorentz(Double_t* x, Double_t* par){

    return par[0]*(par[1]*(x[0]-par[2])*(x[0]-par[2])) / (1. + par[1]*(x[0]-par[2])*(x[0]-par[2])) + par[3];

}

//define lorentz function (fixed function for 0° and 90°)
//provides tau and phi directly
Double_t FitFuncDispersion(Double_t* x, Double_t* par){

    return par[0]* (par[2]*(2*par[2]*par[3]*(x[0]-par[5])*TMath::Sin(2*par[4])-TMath::Cos(2*par[4])+4*par[2]*par[2]*par[3]*par[3]*(x[0]-par[5])*(x[0]-par[5])+1))/(2*(4*par[2]*par[2]*par[3]*par[3]*(x[0]-par[5])*(x[0]-par[5])+1)) + par[1];

}

void FP_Hanle_Macro(Int_t sw, TString data)
{
  ///////////////////////
  // read in *.tab file

  //  TString data = "Data.tab";
  ifstream in;
  in.open(data);
  Float_t t, y, y2;
  vector<Float_t> vt, vy, vy2;
  TString input, lin;

  while (lin.ReadLine(in)){

    istrstream stream(lin.Data());
    stream >> input; t  = input.Atof();
    stream >> input; y  = input.Atof();
    stream >> input; y2 = input.Atof();
    //    cout<<"t "<<t<<"  y "<<y<<"  y2 "<<y2<<endl;
    vt.push_back(t);
    vy.push_back(y);
    vy2.push_back(y2);
  }
  in.close(); 

  ////////////////////////
  // define graphs

  TGraph* ramp;
  TGraph* hanle;
  TGraphErrors* hanleramp;

  Int_t n = vt.size();
  ramp = new TGraph(n);
  hanle = new TGraph(n);


  ////////////////////////
  // fill graphs

  for(int i=0; i<n; i++){
    ramp->SetPoint(i,vt[i],vy2[i]);
    hanle->SetPoint(i,vt[i],vy[i]);
  }

  ///////////////////////
  // linear fit

  Double_t mean = ramp->GetMean();
  // TF1* g = new TF1("gerade","pol1",mean*0.5,mean*2);
  TF1* g = new TF1("gerade","pol1",1,3);
  ramp->Fit(g,"RM");
  
  ////////////////////////
  // fill graph intensity vs B-field in mT

  hanleramp = new TGraphErrors(n);
  Double_t xerr, yerr; ; //relative erros on x,y 
  xerr=0.01;
  yerr=0.01;
  for(int i=0; i<n; i++){
    Double_t time = vt.at(i);
    Double_t current = g->Eval(time);
    current = current*0.0003363*1000.;
    hanleramp->SetPoint(i,current,vy.at(i));
    hanleramp->SetPointError(i,xerr*current,yerr*vy.at(i));  //switch on to use errors (you need to do that to get responsible goodness of fit)
  }

  ////////////////////////
  // get fit function 

  TF1* myfit;
  Double_t low = -0.1;
  Double_t up = 0.1;
  if(sw == 0) myfit = new TF1("lorentz",FitFuncLorentz,low,up,4);
  else if(sw == 1)  myfit = new TF1("dispersion",FitFuncDispersion,low,up,6);
  else{ cout<<"Have to choose the right configuration"<<endl; break; }
  
  ////////////////////////
  // set constants
  Double_t mu_B = 9.27400968E-24;
  Double_t h_bar = 1.05457126E-34;
  Double_t g_J = 1.4838;
  Double_t param = (g_J*mu_B/h_bar)*(1./1E12); //in 1/(mT*ns)

  ////////////////////////
  // set start fit parameters

  if(sw == 0){
    //Example 1
    myfit->SetParameter(0,1);
    myfit->SetParameter(1,1.);
    myfit->SetParameter(2,0);
    myfit->SetParameter(3,0);

    //Example 2
    // myfit->SetParameter(0,-0.4);                                 
    // myfit->SetParameter(1,830.);                               
    // myfit->SetParameter(2,0);                                
    // myfit->SetParameter(3,0.5);                                 
  }  

  if(sw == 1){
    // //myfit->SetParameter(0,-0.1);
    // myfit->SetParameter(0,1);
    // myfit->SetParameter(1,0.5);
    // myfit->SetParameter(2,120);
    // myfit->FixParameter(3,param);
    // myfit->SetParameter(4,0);
    // myfit->SetParameter(5,0);

    //myfit->SetParameter(0,0.02);
    myfit->SetParameter(0,-0.02);
    myfit->SetParameter(1,.1.2);
    myfit->SetParameter(2,120);
    myfit->FixParameter(3,param);
    myfit->SetParameter(4,-1.5);
    myfit->SetParameter(5,-0.02);
  }

  ////////////////////////
  // fitting

  cout <<endl;
  cout <<"Fitting..."<<endl;
  cout <<endl;

  gStyle->SetOptFit(1111);

  cout <<endl;

  TFitResultPtr r = hanleramp->Fit(myfit,"SRM");
  Double_t chi2   = r->Chi2();
  Int_t ndf  = r->Ndf();
  Double_t prob   = r->Prob();

  cout << "Chi2 " << chi2 <<  endl;
  cout << "Ndof " << ndf << endl;
  cout << "Probability " << prob << endl;
  cout <<endl;

  ////////////////////////
  // get values on screen

  if(sw == 0){
    Double_t fwhm = 2.*TMath::Sqrt(1./myfit->GetParameter(1)); 
    cout << "FWHM [mT] = " << fwhm << endl;
    Double_t tau = 1/(param*fwhm);
    cout << "tau [ns] = " << int(tau*10)/10. << endl;
  }
  else if(sw == 1){
    Double_t tau = myfit->GetParameter(2); //GetParError(nr) for errors
    cout << "tau [ns]  = " << int(tau*10)/10. << endl;
    Double_t phi = myfit->GetParameter(4)*360/(2*TMath::Pi());
    cout << "phi [°] = " << int(phi*10)/10. << endl;
  }

  ////////////////////////
  // plot data

  TCanvas* c1 = new TCanvas("ramp", "ramp", 600, 600);
  ramp->GetXaxis()->SetTitle("time");
  ramp->GetYaxis()->SetTitle("current");
  ramp->SetTitle("1. ramp");
  c1->SetBorderMode(0);
  c1->SetGrid();
  c1->SetFillColor(10);
  ramp->Draw("AP");
  c1->SaveAs(data+"_1.png");

  TCanvas* c2 = new TCanvas("hanle", "hanle", 600, 600);
  hanle->GetXaxis()->SetTitle("time");
  hanle->GetYaxis()->SetTitle("intensity");
  hanle->SetTitle("2. hanle");
  c2->SetBorderMode(0);
  c2->SetGrid();
  c2->SetFillColor(10);
  hanle->Draw("AP");
  c2->SaveAs(data+"_2.png");

  TCanvas* c3 = new TCanvas("fit", "fit", 600, 600);
  myfit->GetXaxis()->SetTitle("current");
  myfit->GetYaxis()->SetTitle("intensity");
  myfit->SetTitle("3. fit");
  c3->SetBorderMode(0);
  c3->SetGrid();
  c3->SetFillColor(10);
  //  myfit->Draw("ACP");
  myfit->Draw();
  c3->SaveAs(data+"_3.png");

  TCanvas* c4 = new TCanvas("hanleramp", "hanleramp", 600, 600);
  hanleramp->GetXaxis()->SetTitle("current");
  hanleramp->GetYaxis()->SetTitle("intensity");
  hanleramp->SetTitle("4. hanleramp");
  c4->SetBorderMode(0);
  c4->SetGrid();
  c4->SetFillColor(10);
  hanleramp->Draw("AP");
  c4->SaveAs(data+"_4.png");

  TFile* f_out = new TFile(data+".root","RECREATE");
  c1->Write();
  c2->Write();
  c3->Write();
  c4->Write();
  f_out->Close();

}


void Extrapol(){

  Double_t T[3] = {10.,-1.,-8.};
  Double_t x[3];
  for(int i=0;i<3;i++){
    x[i] = TempSub(T[i]);
  }
  Double_t y[3] = {103.3,96.6,96};

  TGraph* mygraph = new TGraph(3,x,y);
  mygraph->SetMarkerStyle(5);
  mygraph->SetMarkerSize(2);
  mygraph->Draw("AP");
}

Double_t TempSub(Double_t T){

  Double_t T2 = 273.+T;
  Double_t pc = 167000000.;
  Double_t Tc = 1764.;
  // Double_t pc = 174000000.;
  // Double_t Tc = 1476.;
  Double_t Tr = 1.-T2/Tc;
  Double_t a1 = -4.57618368;
  Double_t a2 = -1.40726277;
  Double_t a3 = 2.36263541;
  Double_t a4 = -31.0889985;
  Double_t a5 = 58.0183959;
  Double_t a6 = -27.6304546;

  Double_t p = 1.;
  p = 1000.*pc*exp((Tc/T2)*(a1*Tr+a2*pow(Tr,1.89)+a3*pow(Tr,2.)+a4*pow(Tr,8)+a5*pow(Tr,8.5)+a6*pow(Tr,9.)));
  cout<<"T "<<T<<" p "<<p<<endl;
  return p;

}
