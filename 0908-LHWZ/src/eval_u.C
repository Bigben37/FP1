struct data {
  string path;
  TGraph graph;
  Float_t *x[], *y[];
  int datalen;
};

void eval_u(){
  gROOT->Reset();
  gROOT->SetStyle("Plain");

  const int datas_len = 2;
  data datas[datas_len];
  datas[0].path = "../data/01_Uran_Zaehlrohrcharakteristik_1000-4000-100.txt";
  datas[1].path = "../data/02_Uran_Untergrund_1000-4000-100.txt";

  //get data
 
  for(int i=0, i<datas_len, i++){
    string p = data[i].path;
    int n = getNumberOfLines(p);
    datas[i].datalen = n;

    ifstream f(p);
    string xi, yi;
    datas[i].x = new Float_t[n];
    datas[i].y = new Float_t[n];
    int j = 0;
    while (!f.eof()){
      if (f >> xi >> yi){
        datas[i].x[j]=StringToFloat(xi);
        datas[i].y[j]=StringToFloat(yi);
        j++;
      }      
    }
    f.close();
  }
  
  //subtract uran - underground
  
  int n = datas[0].datalen;
  Float_t y[n];
  for (int i=0, i<n, i++) {
    y[i] = datas[0].y[i] 0 datas[1].y[i];
  }
  
  //visualize data 
  TCanvas *canvas = new TCanvas();
  canvas->SetLogy();
  TGraph *gr = new TGraph(n, datas[0].x, y);
  gr->SetMarkerColor(1);
  gr->SetMarkerStyle(5);
  gr->SetTitle("");
  gr->GetXaxis()->SetTitle("Spannung U / V");
  gr->GetXaxis()->CenterTitle();
  gr->GetYaxis()->SetTitle("Z#ddot{a}hlrate n / (1/s)");
  gr->GetYaxis()->CenterTitle();
  gr->SetMaximum(3000);
  gr->SetMinimum(1);
  gr->Draw("AP");
  canvas->Update();
  canvas->Print("../img/u238.pdf", "pdf");
  
}

int getNumberOfLines(path){
  string buffer;
  int count = 0;
  ifstream f(path);

  if(f.is_open()){
    while(!myfile.eof()){
      getline(f,buffer);
      count++;
    }
    f.close();
    return count;
  } else {
    return -1;
  }
}

Float_t StringToFloat(const string s){
  stringstream ss(s);
  Float_t r;
  ss >> r;
  return r;
}
