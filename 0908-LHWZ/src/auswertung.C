void auswertung(){
  gROOT->Reset();
  gROOT->SetStyle("Plain");

  //get data  

  ifstream in;
  in.open("../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt");
  
  string s, t;
  const Int_t n = 31;
  Float_t x[n], y[n];
  
  Int_t i=0;
  while (!in.eof()){
    if (in >> s >> t){
      cout << StringToFloat(s) <<  ":" << StringToFloat(t) <<endl;
      x[i]=StringToFloat(s);
      y[i]=StringToFloat(t);
      i++;
    }
  }

  in.close();

  //show data
  TCanvas *canvas = new TCanvas("canvas","A Simple Graph Example");
  canvas->SetLogy();
  TGraph *gr = new TGraph(n, x, y);
  gr->SetMarkerColor(1);
  gr->SetMarkerStyle(5);
  gr->SetTitle("");
  gr->GetXaxis()->SetTitle("Spannung U / V");
  gr->GetXaxis()->CenterTitle();
  gr->GetYaxis()->SetTitle("Z#ddot{a}hlrate n / (1/s)");
  gr->GetYaxis()->CenterTitle();
  gr->SetMaximum(3000);
  gr->SetMinimum(20);
  gr->Draw("AP");
  canvas->Update();
  canvas->Print("test.pdf", "pdf");
}

Float_t StringToFloat(const string s){
  stringstream ss(s);
  Float_t r;
  ss >> r;
  return r;
}
