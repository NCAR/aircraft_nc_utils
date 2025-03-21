
package edu.ucar.eol.nc2asc;


import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Frame;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;
import java.awt.ScrollPane;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.Calendar;
import java.util.zip.DataFormatException;

import javax.swing.AbstractButton;
import javax.swing.BorderFactory;
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.border.Border;

import edu.ucar.eol.nc2ascData.DataFmt;
//import edu.ucar.eol.nc2ascData.NCData;


class NC2AUIDiag extends JDialog {
	static final long serialVersionUID = 0;

	//assumed MISSVAL for all variables is -32768;
	//assumed the time variable contains the start-time in seconds since1970
	//and each record is 1 second apart from previous one

	private final static String CBDATE = "CBDATE";
	private final static String CBTM = "CBTM";
	private final static String RDMTR = "RDMTR";
	private final static String RDMTR2 = "RDMTR2";
	private final static String RVAL = "RVAL";
	private final static String RVAL2 = "RVAL2";
	private final static String RVAL3 = "RVAL3";
	private final static String RTMSET = "RTMSET";
	private final static String RTMSET2 = "RTMSET2";
	private final static String RHEAD1 = "RHEAD1";
	private final static String RHEAD2 = "RHEAD2";
	private final static String RHEAD3 = "RHEAD3";
	private final static String RHEAD4 = "RHEAD4";

	private JRadioButton 	rDmtr, rDmtr2, rVal, rVal2, rVal3, rTmSet, rTmSet2,
				rHead1, rHead2, rHead3, rHead4;
	private JComboBox    	cbDate, cbTm;
	private JTextField 	tfTmSet, tfTmSet2, tfDateSet, tfDateSet2, tfSmpRate; 
	private JTextArea 	tfDisp; 

	private DataFmt  dFormat = null; //data format chosen by author
	//	private NCData   ncdata =null;
	private String[] cbDateTxt, cbTmTxt;
	private String[] dDisp   = new String[10]; //make up data for preview display

	private int  highRate;
	private int  size;
	private long tmStart;
	private String[] origTm= new String[4];

	public NC2AUIDiag(Frame owner, boolean modal) {
		super(owner, modal);
		JDialog.setDefaultLookAndFeelDecorated(true);

		init();
	}

	public NC2AUIDiag(Frame owner, boolean modal, String[] initData, DataFmt df, long[] gDataInf) {
		super(owner, modal);
		JDialog.setDefaultLookAndFeelDecorated(true);
		this.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);

		dDisp=initData;
		highRate = (int)gDataInf[0];
		tmStart =   gDataInf[1];
		size   = (int)gDataInf[2];
		dFormat = df;
		initTmSet();
		init();

		displaySelFmt(); //display user selected format
		tfDisp.setText(refreshPreview());
	}
	public void setDispData(String[] dd){
		dDisp=dd;
		if (tfDisp==null){
			NC2Act.wrtMsg("Text field in the format dialog is not created");
			return;
		}
		int i=0;
		for (i=0; i< dd.length; i++){
			//nc2asc.NC2Act.wrtMsg("tfdisp data:"+dd[i]);
			tfDisp.insert(dd[i], i++);
		}
	}

	public DataFmt getDFormat() {
		return dFormat;
	}


	public JPanel createPaneTm() {

		JPanel jpTm  = new JPanel();
		jpTm.setLayout(new GridLayout(0,1));

		Border bdTm = BorderFactory.createTitledBorder(" Date-Time Format  ");   
		jpTm.setBorder(bdTm);
		cbDateTxt = new String[3];
		cbDateTxt[0]=DataFmt.DATEDASH;
		cbDateTxt[1]=DataFmt.DATESPACE;
		cbDateTxt[2]=DataFmt.NODATE;
		cbDate = new JComboBox(cbDateTxt);
		cbDate.setActionCommand(CBDATE);
		cbDate.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e){
				selectDateFrmt(e);
			}
		});
		jpTm.add(cbDate);

		cbTmTxt = new String[4];
		cbTmTxt[0]=DataFmt.TIMECOLON;
		cbTmTxt[1]=DataFmt.TIMESPACE;
		cbTmTxt[2]=DataFmt.TIMENOSPACE;
		cbTmTxt[3]=DataFmt.TIMESEC;

		cbTm = new JComboBox(cbTmTxt);
		jpTm.add(cbTm);
		cbTm.setActionCommand(CBTM);
		cbTm.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e){
				selectTmFrmt(e);
			}
		});

		return jpTm;		
	}

	public JPanel createPaneHead() {
		JPanel jpHead  = new JPanel();
		//	jpHead.setFont(Systems, 7);
		jpHead.setLayout(new GridLayout(0,1));

		Border bdHead = BorderFactory.createTitledBorder("Header");
		jpHead.setBorder(bdHead);

		rHead1 = new JRadioButton(DataFmt.HDR_PLAIN);
		jpHead.add(rHead1);
		rHead1.setSelected(true);
		addButtonActCmd(rHead1, RHEAD1);

		rHead2 = new JRadioButton(DataFmt.HDR_AMES); 
		jpHead.add(rHead2);
		addButtonActCmd(rHead2, RHEAD2);

		rHead3 = new JRadioButton(DataFmt.HDR_ICARTT); 
		jpHead.add(rHead3);
		addButtonActCmd(rHead3, RHEAD3);

		rHead4 = new JRadioButton(DataFmt.HDR_NCML); 
		jpHead.add(rHead4);
		addButtonActCmd(rHead4, RHEAD4);
		rHead4.setEnabled(false);

                ButtonGroup group = new ButtonGroup();
                group.add(rHead1);
                group.add(rHead2);
                group.add(rHead3);
                group.add(rHead4);

		jpHead.add(createPaneSR());
		return jpHead;
	}

	public JPanel createPaneSR() {
		JPanel jpSmpRate = new JPanel();
		jpSmpRate.setLayout(new GridLayout(0,2));
		tfSmpRate = new JTextField("1");
		JLabel l = new JLabel("Avg: ");
		jpSmpRate.add(l);
		jpSmpRate.add(tfSmpRate);
		tfSmpRate.addKeyListener( new KeyListener() {
			public void keyPressed(KeyEvent e) {};
			public void keyReleased(KeyEvent e) {
				String srStr= tfSmpRate.getText().trim();
				if (srStr.isEmpty()) {return;}
				dFormat.setDataFmt(srStr, DataFmt.AVG_IDX);
				tfDisp.setText(refreshPreview());
			};
			public void keyTyped(KeyEvent e) {};
		});
		//addSmpRateFocusListener();
		return jpSmpRate;
	}

	public JPanel createPaneDmtr() {
		JPanel jpDmtr  = new JPanel();
		jpDmtr.setLayout(new GridLayout(0,1));
		//tfDisp.insert(dDisp[i], i);

		Border bdDmtr = BorderFactory.createTitledBorder("Delimiter");
		jpDmtr.setBorder(bdDmtr);

		rDmtr = new JRadioButton("Comma");
		jpDmtr.add(rDmtr);
		rDmtr.setSelected(true);
		addButtonActCmd(rDmtr, RDMTR);

		rDmtr2 = new JRadioButton("Space"); 
		jpDmtr.add(rDmtr2);
		addButtonActCmd(rDmtr2, RDMTR2);

                ButtonGroup group = new ButtonGroup();
                group.add(rDmtr);
                group.add(rDmtr2);

		return jpDmtr;
	}

	public JPanel createPaneVal() {
		JPanel jpVal  = new JPanel();
		jpVal.setLayout(new GridLayout(0,1));

		Border bdVal = BorderFactory.createTitledBorder("Fill Value");
		jpVal.setBorder(bdVal);

		rVal = new JRadioButton(DataFmt.FILLVALUE);
		jpVal.add(rVal);
		rVal.setSelected(true);
		addButtonActCmd(rVal, RVAL);

		rVal2 = new JRadioButton(DataFmt.LEAVEBLANK); 
		jpVal.add(rVal2);
		addButtonActCmd(rVal2, RVAL2);

		rVal3 = new JRadioButton(DataFmt.REPLICATE); 
		jpVal.add(rVal3);
		addButtonActCmd(rVal3, RVAL3);

                ButtonGroup group = new ButtonGroup();
                group.add(rVal);
                group.add(rVal2);
                group.add(rVal3);

		return jpVal;
	}

	public JPanel createPaneTmSet() {

		JPanel jpTmSet  = new JPanel();
		jpTmSet.setLayout(new GridLayout(0,1));

		rTmSet = new JRadioButton("Full"); 
		rTmSet.setSelected(true);
		jpTmSet.add(rTmSet);

		rTmSet2 = new JRadioButton("Partial Scale"); 
		jpTmSet.add(rTmSet2);

		JPanel jp = new JPanel();
		jp.setLayout(new GridLayout(0,2));
		tfDateSet = new JTextField(origTm[0]);
		tfDateSet.setSize(12,8);
		tfDateSet.setEnabled(false); 
		tfTmSet = new JTextField(origTm[1]);
		tfTmSet.setSize(12,8);
		tfTmSet.setEnabled(false); 
		jp.add(tfDateSet);
		jp.add(tfTmSet);
		jpTmSet.add(jp);

		jp = new JPanel();
		jp.setLayout(new GridLayout(0,2));
		tfDateSet2 = new JTextField(origTm[2]);
		tfDateSet2.setSize(12,8);
		tfDateSet2.setEnabled(false); 
		tfTmSet2 = new JTextField(origTm[3]);		
		tfTmSet2.setSize(12,8);
		tfTmSet2.setEnabled(false);
		//lblEnd = new JLabel("End"); lblEnd.setEnabled(false);
		//jp.add(lblEnd); 
		//jp.add(tfTmSet2);
		jp.add(tfDateSet2);
		jp.add(tfTmSet2);
		jpTmSet.add(jp);
		Border bdDmtr = BorderFactory.createTitledBorder("Time Scope");
		jpTmSet.setBorder(bdDmtr);

		addButtonActCmd(rTmSet, RTMSET);
		addButtonActCmd(rTmSet2, RTMSET2);
		addTmSetFocusListener();
		addTmSet2FocusListener();
		return jpTmSet;
	}


	public ScrollPane createPaneTxtArea() {

		String disp="";

		//if the demo data is empty, set defaults.
		if (dDisp[0]==null || dDisp[0].length()==0) {
			NC2Act.wrtMsg("Input demo data is empty...");
			dDisp[0]="Date,Start_UTC,A1DC_LWO,A2DC_LWO";
			String s1 = "2007-5-16,23:44:";
			String s2 = DataFmt.COMMAVAL + DataFmt.MISSVAL + DataFmt.COMMAVAL+",0.0";
			int sec = 17;
			for (int i=1; i<10; i++) {
				sec++;
				dDisp[i]=s1+sec+s2;
			}
		}

		disp= refreshPreview();

		tfDisp = new JTextArea(disp);
		tfDisp.setPreferredSize(new Dimension(500, 600));
		tfDisp.setLineWrap(true);
		tfDisp.setEditable(false);
		tfDisp.setFont(new Font("System", Font.ITALIC,  16));
		tfDisp.setVisible(true);
		tfDisp.setBorder(BorderFactory.createLineBorder(Color.blue));
		ScrollPane sp = new ScrollPane();
		sp.setSize(300, 250);
		sp.add(tfDisp);
		return sp;
	}


	private JPanel createButtons() {
		JButton bnOk = new JButton("Ok");
		JButton bnCancel = new JButton("Cancel");
		JPanel jp = new JPanel();
		jp.setLayout(new GridLayout(0,7));
		jp.add(new JLabel());
		jp.add(new JLabel());
		jp.add(new JLabel());
		jp.add(new JLabel());
		jp.add(new JLabel());
		jp.add(bnCancel);
		jp.add(bnOk);

		addButtonActCmd(bnOk, "ok");
		addButtonActCmd(bnCancel, "cancel");

		return jp;
	}

	private void init() {

		try {
			this.setTitle("         Data Format Dialog          ");
			this.setLayout(new GridBagLayout());
			GridBagConstraints c = new GridBagConstraints();
			c.fill = GridBagConstraints.HORIZONTAL;
			c.weighty = 1.0; 
			c.weightx = 0.5;
			c.insets= new Insets(15,0,0,0);
			c.anchor=GridBagConstraints.NORTH;
			int i=0;

			//add head
			c.gridx = i++;
			c.gridy = 0;
			this.getContentPane().add(createPaneHead(), c); 

			//add date-time
			c.gridx = i++;
			c.gridy = 0;
			this.add(createPaneTm(), c); 

			//add dlimiter
			c.gridx = i++;
			this.add(createPaneDmtr(), c);

			//add missing val
			c.gridx = i++; 
			this.add(createPaneVal(), c);

			//add time scope
			c.gridx = i++;
			this.add(createPaneTmSet(), c);

			//add txt display
			c.gridx = 0;
			c.gridy = 1;
			c.gridheight= 1;
			c.gridwidth= GridBagConstraints.REMAINDER;
			this.add(createPaneTxtArea(), c);

			//add cancel and ok buttons
			c.gridy = 2;
			c.gridwidth= GridBagConstraints.REMAINDER;
			c.anchor = GridBagConstraints.SOUTHEAST;
			this.add(createButtons(),c);

		} catch (Exception e) {
			NC2Act.wrtMsg("Err in init_method: "+e.getMessage());
		}

		//chk high rate or low rate data to control options
		if (highRate>1) {
			tfSmpRate.setEnabled(false);
		} else {
			rVal3.setEnabled(false);
		}
	}


	/**
	 *  actions listener
	 */
	void addButtonActCmd(AbstractButton jb, String actStr){
		jb.setActionCommand(actStr);
		jb.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e){
				selectDelimiterComma(e);
				selectDelimiterSpace(e);
				selectValFrmt(e);
				selectValFrmt2(e);
				selectValFrmt3(e);
				selectTmSetFrmt(e);
				selectTmSetFrmt2(e);
				selectHead1(e);
				selectHead2(e);
				selectHead3(e);
				selectHead4(e);
				selectCancel(e);
				selectOk(e);

			}
		});
	}


	void addTmSetFocusListener() {
		tfTmSet.addFocusListener ( new FocusListener() {
			public void focusGained(FocusEvent e) {};
			public void focusLost(FocusEvent e) {
				chkStartTmField();
				tfDisp.setText(refreshPreview());	
			}
		});
	}

	void addTmSet2FocusListener() {
		tfTmSet2.addFocusListener ( new FocusListener() {
			public void focusGained(FocusEvent e) {};
			public void focusLost(FocusEvent e) {
				chkEndTmField(); 
			}
		});
	}


	private void chkStartTmField() {
		String dt = tfDateSet.getText();
		String tm = tfTmSet.getText();
		long tmms= getNewTmMilSec(dt,tm, 0);

		if (tmms+1000 < tmStart){
			NC2Act.wrtMsg("This time is earlier than the start-time: " + origTm[0]+ " "+ origTm[1]);
			tfDateSet.setText(origTm[0]);
			tfTmSet.setText(origTm[1]);
			return;
		}
		long tmEnd = getNewTmMilSec(tfDateSet2.getText().trim(),tfTmSet2.getText().trim(), 1);
		dFormat.setDataFmt(tmms+ DataFmt.TMSETDELIMIT+(int)((tmEnd-tmms)/1000), DataFmt.TMSET_IDX);
		dFormat.setTmSet(tfDateSet.getText().trim()+ DataFmt.COMMAVAL + tfTmSet.getText().trim()+DataFmt.TMSETDELIMIT+ tfDateSet2.getText().trim()+ DataFmt.COMMAVAL + tfTmSet2.getText().trim()  );
	}


	private void chkEndTmField() {
		//new end-time
		String dt = tfDateSet2.getText();
		String tm = tfTmSet2.getText();

		long tmEnd = getNewTmMilSec(dt,tm, 1);
		if ((int)tmEnd/1000 > (int)(tmStart+size*1000)/1000){
			NC2Act.wrtMsg("The time is later than the end-time: " + origTm[2]+ " "+ origTm[3]);
			tfDateSet2.setText(origTm[2]);
			tfTmSet2.setText(origTm[3]);
			return;
		}

		//compare with new-start 
		String dt0 = tfDateSet.getText();
		String tm0 = tfTmSet.getText();
		long tmStart= getNewTmMilSec(dt0,tm0, 0);
		if (tmStart > tmEnd){
			NC2Act.wrtMsg("The end-time is less than the start-time: " );
			tfDateSet.setText(origTm[0]);
			tfTmSet.setText(origTm[1]);
			tfDateSet2.setText(origTm[2]);
			tfTmSet2.setText(origTm[3]);
			return;
		}
		//start-time(milsec) and range-seconds
		dFormat.setDataFmt(tmStart+ DataFmt.TMSETDELIMIT+(int)((tmEnd-tmStart)/1000), DataFmt.TMSET_IDX);
		dFormat.setTmSet(tfDateSet.getText().trim()+ DataFmt.COMMAVAL + tfTmSet.getText().trim()+DataFmt.TMSETDELIMIT+ tfDateSet2.getText().trim()+ DataFmt.COMMAVAL + tfTmSet2.getText().trim()  );
	}


	private long getNewTmMilSec(String dt, String tm, int idx)  {

		String[] dts = dt.split("-");
		String[] tms = tm.split(":");
		if (dts.length!=3 || tms.length !=3) {
			NC2Act.wrtMsg("Invalid Tm Data format...");
			if (idx ==0){
				tfDateSet.setText(origTm[0]);
				tfTmSet.setText(origTm[1]);
			} else {
				tfDateSet2.setText(origTm[2]);
				tfTmSet2.setText(origTm[3]);
			}
		}

		Calendar cl = Calendar.getInstance();
		int yy = Integer.parseInt(dts[0]);
		int mm = Integer.parseInt(dts[1]);
		int dd = Integer.parseInt(dts[2]);
		int h = Integer.parseInt(tms[0]);
		int m = Integer.parseInt(tms[1]);
		int s = Integer.parseInt(tms[2]);

		yy = 1900+yy;
		if (yy< 1950) {yy = 100 +yy;} //1950 -1999  or 2000- now

		cl.set(yy,mm,dd,h,m,s);
		return cl.getTimeInMillis();
	}

	void selectCancel(ActionEvent e){
		if ("cancel".equals(e.getActionCommand())) {
			dFormat.initDataFmt();
			//dFormat.showDataFmt();
			dispose();
		}
	}

	void selectOk(ActionEvent e){
		if ("ok".equals(e.getActionCommand())) {
			//chkEndTmField();
			dispose();
		}
	}

	void selectDateFrmt(ActionEvent e) {
		if (CBDATE.equals(e.getActionCommand())) {
			dFormat.setDataFmt(cbDateTxt[cbDate.getSelectedIndex()],DataFmt.DATE_IDX);
			tfDisp.setText(refreshPreview());	
		}
	}

	void selectTmFrmt(ActionEvent e) {
		if (CBTM.equals(e.getActionCommand())) {
			dFormat.setDataFmt(cbTmTxt[cbTm.getSelectedIndex()], DataFmt.TM_IDX);
			tfDisp.setText(refreshPreview());
		}
	}

	void selectDelimiterComma(ActionEvent e) {
		if (RDMTR.equals(e.getActionCommand())) {
			if (rDmtr.isSelected()) {
				rDmtr2.setSelected(false);
				rVal2.setEnabled(true);
				dFormat.setDataFmt(DataFmt.COMMAVAL, DataFmt.DMTR_IDX);
				tfDisp.setText(refreshPreview());
			}
		}
	}

	void selectDelimiterSpace(ActionEvent e) {
		if (RDMTR2.equals(e.getActionCommand())) {
			if (rDmtr2.isSelected()) {
				rDmtr.setSelected(false);
				dFormat.setDataFmt(" ", DataFmt.DMTR_IDX);

				rVal2.setEnabled(false);
				rVal2.setSelected(false);
				String mval = dFormat.getDataFmt()[DataFmt.MVAL_IDX];
				if (mval==null || mval.isEmpty()) {
					rVal.setSelected(true);
					dFormat.setDataFmt(DataFmt.MISSVAL, DataFmt.MVAL_IDX);
				}
				tfDisp.setText(refreshPreview());
			}
		}
	}


	void selectValFrmt(ActionEvent e) {
		if (RVAL.equals(e.getActionCommand())) {
			if (rVal.isSelected()) {
				rVal2.setSelected(false);
				rVal3.setSelected(false);
				dFormat.setDataFmt(DataFmt.MISSVAL, DataFmt.MVAL_IDX);
				tfDisp.setText(refreshPreview());
			}

		}
	}


	void selectValFrmt2(ActionEvent e) {
		if (RVAL2.equals(e.getActionCommand())) {	
			if (rVal2.isSelected()) {
				rVal.setSelected(false);
				rVal3.setSelected(false);
				dFormat.setDataFmt("", DataFmt.MVAL_IDX);
				tfDisp.setText(refreshPreview());
			}	
		}
	}


	void selectValFrmt3(ActionEvent e) {
		if (RVAL3.equals(e.getActionCommand())) {	
			if (rVal3.isSelected()) {
				rVal.setSelected(false);
				rVal2.setSelected(false);
				dFormat.setDataFmt(DataFmt.REPLICATE, DataFmt.MVAL_IDX);
				tfDisp.setText(refreshPreview());
			}	
		}
	}

	void selectTmSetFrmt(ActionEvent e) {
		if (RTMSET.equals(e.getActionCommand())) {	
			if (rTmSet.isSelected()) {
				rTmSet2.setSelected(false);
				tfTmSet.setEnabled(false);
				tfTmSet2.setEnabled(false);
				tfDateSet.setEnabled(false);
				tfDateSet2.setEnabled(false);
				//lblStart.setEnabled(false);
				//lblEnd.setEnabled(false);
				dFormat.setDataFmt(DataFmt.FULLTM, DataFmt.TMSET_IDX);
			}
		}
	}

	void selectTmSetFrmt2(ActionEvent e) {
		if (RTMSET2.equals(e.getActionCommand())) {	
			if (rTmSet2.isSelected()) {
				rTmSet.setSelected(false);
				tfTmSet.setEnabled(true);
				tfTmSet2.setEnabled(true);
				tfDateSet.setEnabled(true);
				tfDateSet2.setEnabled(true);
				//lblStart.setEnabled(true);
				//lblEnd.setEnabled(true);
				//DataFmt.setDataFmt(tfTmSet.getText()+DataFmt.TMSETDELIMIT+tfTmSet2.getText(), DataFmt.TMSET_IDX);
			}
		}
	}

	void selectHead1(ActionEvent e){
		if (RHEAD1.equals(e.getActionCommand())) {	
			if (rHead1.isSelected()) {
				rHead2.setSelected(false);
				rHead3.setSelected(false);
				rHead4.setSelected(false);
				cbTm.setEnabled(true);
				cbDate.setEnabled(true);
				rDmtr.setEnabled(true);
				rDmtr2.setEnabled(true);
				rVal.setEnabled(true);
				rVal2.setEnabled(true);
				rVal3.setEnabled(true);

				//dForamt[5]=RHEAD1;
				dFormat.setDataFmt(DataFmt.HDR_PLAIN, DataFmt.HEAD_IDX);
			}

		}
	}

	void selectHead2(ActionEvent e){
		if (RHEAD2.equals(e.getActionCommand())) {	
			if (rHead2.isSelected()){
				rHead1.setSelected(false);
				rHead3.setSelected(false);
				rHead4.setSelected(false);
				dFormat.setDataFmt(DataFmt.HDR_AMES, DataFmt.HEAD_IDX);

				//noDate secofday
				cbTm.setSelectedIndex(3); //display secofday
				cbDate.setSelectedIndex(2);
				dFormat.setDataFmt(cbTmTxt[cbTm.getSelectedIndex()], DataFmt.TM_IDX);
				dFormat.setDataFmt(cbDateTxt[cbDate.getSelectedIndex()], DataFmt.DATE_IDX);
				cbTm.setEnabled(false);
				cbDate.setEnabled(false);

				//delimiter = space
				rDmtr.setSelected(false);
				rDmtr2.setSelected(true);
				dFormat.setDataFmt(DataFmt.SPACEVAL, DataFmt.DMTR_IDX);
				rDmtr.setEnabled(false);
				rDmtr2.setEnabled(false);

				//fill value =FILLVal
				rVal.setSelected(true);
				rVal2.setSelected(false);
				rVal3.setSelected(false);
				dFormat.setDataFmt(DataFmt.MISSVAL, DataFmt.MVAL_IDX);
				rVal.setEnabled(false);
				rVal2.setEnabled(false);
				rVal3.setEnabled(false);

				tfDisp.setText(refreshPreview());
			}
		}
	}

	void selectHead3(ActionEvent e){
		if (RHEAD3.equals(e.getActionCommand())) {	
			if (rHead3.isSelected()) {
				rHead1.setSelected(false);
				rHead2.setSelected(false);
				rHead4.setSelected(false);
				dFormat.setDataFmt(DataFmt.HDR_ICARTT, DataFmt.HEAD_IDX);

				//noDate secofday
				cbTm.setSelectedIndex(3); //display secofday
				cbDate.setSelectedIndex(2);
				dFormat.setDataFmt(cbTmTxt[cbTm.getSelectedIndex()], DataFmt.TM_IDX);
				dFormat.setDataFmt(cbDateTxt[cbDate.getSelectedIndex()], DataFmt.DATE_IDX);
				cbTm.setEnabled(false);
				cbDate.setEnabled(false);

				//delimiter = space
				rDmtr.setSelected(true);
				rDmtr2.setSelected(false);
				dFormat.setDataFmt(DataFmt.COMMAVAL, DataFmt.DMTR_IDX);
				rDmtr.setEnabled(false);
				rDmtr2.setEnabled(false);

				//fill value =FILLVal
				rVal.setSelected(true);
				rVal2.setSelected(false);
				rVal3.setSelected(false);
				dFormat.setDataFmt(DataFmt.MISSVAL, DataFmt.MVAL_IDX);
				rVal.setEnabled(false);
				rVal2.setEnabled(false);
				rVal3.setEnabled(false);

				tfDisp.setText(refreshPreview());
			}
		}
	}

	void selectHead4(ActionEvent e){
		if (RHEAD4.equals(e.getActionCommand())) {
			if (rHead4.isSelected()) {
				rHead1.setSelected(false);
				rHead2.setSelected(false);
				rHead3.setSelected(false);
				cbTm.setEnabled(true);
				cbDate.setEnabled(true);
				cbTm.setEnabled(true);
				cbDate.setEnabled(true);
				rDmtr.setEnabled(true);
				rDmtr2.setEnabled(true);
				rVal.setEnabled(true);
				rVal2.setEnabled(true);
				rVal3.setEnabled(true);
				dFormat.setDataFmt(DataFmt.HDR_NCML, DataFmt.HEAD_IDX);

				tfDisp.setText(refreshPreview());
			}
		}
	}

	void addSmpRateFocusListener() {
		tfSmpRate.addFocusListener ( new FocusListener() {
			public void focusGained(FocusEvent e) {};
			public void focusLost(FocusEvent e) {
				String srStr="";
				try {
					srStr= tfSmpRate.getText().trim();
				} catch (Exception en) {
					tfSmpRate.setText("1");
				}
				if (srStr==null || srStr.isEmpty()) {
					tfSmpRate.setText("1");
				} else 	{
					dFormat.setDataFmt(srStr, DataFmt.AVG_IDX);
					tfDisp.setText(refreshPreview());
				}				
			}
		});
	}


	/**
	 * Update Select Data Format sub window which shows the anticipated output.
	 */
	private String  refreshPreview() {
		String[] ddata = new String[10];

		//check new start time
		if (tfDateSet.isEnabled()) {
			ddata[0]="Date,Start_UTC,A1DC_LWO,A2DC_LWO";
			String[] tt = tfTmSet.getText().split(":");
			String s1 = tfDateSet.getText()+DataFmt.COMMAVAL+ tt[0]+":"+tt[1]+":";
			//add 19 0r 20
			if (Integer.parseInt(s1.split("-")[0]) < 50) {
				s1 = "20" + s1;
			} else {
				s1 += "19" + s1;
			}
			String s2 = DataFmt.COMMAVAL + ",0.0";
			int sec = Integer.parseInt(tt[2]);
			for (int i = 1; i < 10; i++) {
				ddata[i] = s1+sec+s2;
				sec++;
			}
		} else {
			ddata = dDisp;
		}

		// check avg
		if (tfSmpRate.isEnabled() && tfSmpRate.getText() != null) {
			if (tfSmpRate.getText().isEmpty()){
				tfSmpRate.setText("1");
			}
			int avg = Integer.parseInt(tfSmpRate.getText().trim());
			if (avg > 1)	{
				return resetAvgDisp(ddata);
			}
		}

		// handle date/time
		String tmp = ddata[0];
		tmp = dFormat.fmtDmtr(tmp) + "\n";

		// handle date/time and two demo data-items
		for (int i = 1; i < ddata.length; i++){

			String[] d = ddata[i].split(DataFmt.COMMAVAL);
			try { 
				d[0]=dFormat.fmtDate(d[0].split("-"));
				d[1]=dFormat.fmtTm(d[1].split(":"));
			} catch (DataFormatException de) {
				return "Data Format Exception"+de.getMessage();
			}

			String onedata = dFormat.fmtDmtr(d);
			tmp += onedata + "\n";
		}
		return tmp;
	}

	private String resetAvgDisp(String[] ddata) {
		int avg = Integer.parseInt(tfSmpRate.getText().trim());

		int loop = ddata.length;
		int len =  (int)loop/avg;

		String ret =   dFormat.fmtDmtr(ddata[0]);
		for (int i =0; i<len; i++) {
			String[] one = ddata[i*avg+1].split(DataFmt.COMMAVAL);

			//adjust time
			long ms = getNewTmMilSec(one[0], one[1],0);
			long tot = 0;
			for (int j=0; j<avg; j++) {
				tot = tot+ ms + j*1000;
			}
			tot = tot/avg;
			Calendar cl = Calendar.getInstance();
			cl.setTimeInMillis(tot);

			//get new time 
			one[0]=  cl.get(Calendar.YEAR)+ "-"+ cl.get(Calendar.MONTH) + "-"+cl.get(Calendar.DAY_OF_MONTH);
			one[1]=  cl.get(Calendar.HOUR_OF_DAY)+ ":"+ cl.get(Calendar.MINUTE) + ":"+cl.get(Calendar.SECOND);

			try {
				one[0] = dFormat.fmtDate(one[0]);
				one[1] = dFormat.fmtTm(one[1]);
				one[1] += "."+cl.get(Calendar.MILLISECOND);
			} catch (DataFormatException e) {
				NC2Act.wrtMsg("resetAvgDisp_fmtDate_fmtTm exception..."+e.getStackTrace());
			}
			ret += "\n" + dFormat.fmtDmtr(one);
		}

		//add extra empty lines
		for (int i=0; i<loop-len; i++){
			ret += " \n";
		}
		return ret;
	}



	void initTmSet() {
		Calendar cl = Calendar.getInstance();
		cl.setTimeInMillis(tmStart);

		origTm[0] = cl.get(Calendar.YEAR)+ "-"+ cl.get(Calendar.MONTH)+"-"+cl.get(Calendar.DAY_OF_MONTH);
		origTm[0] = origTm[0].substring(2);	//chop off the first 2 chars 19 or 20
		origTm[1] = cl.get(Calendar.HOUR_OF_DAY )+ ":"+ cl.get(Calendar.MINUTE)+":"+cl.get(Calendar.SECOND);

		cl.add(Calendar.SECOND, size);
		origTm[2] = cl.get(Calendar.YEAR)+ "-"+ cl.get(Calendar.MONTH)+"-"+cl.get(Calendar.DAY_OF_MONTH);
		origTm[2] = origTm[2].substring(2);	//chop off the first 2 chars 19 or 20
		origTm[3] = cl.get(Calendar.HOUR_OF_DAY)+ ":"+ cl.get(Calendar.MINUTE)+":"+cl.get(Calendar.SECOND);
	}

	void displaySelFmt() {
		//get fmt re-display format
		String[] dfmt = dFormat.getDataFmt();

		rHead1.setSelected(false);
		rHead2.setSelected(false);
		rHead3.setSelected(false);
		rHead4.setSelected(false);

		if (highRate > 1) {
			rHead1.setSelected(true);
			rHead2.setEnabled(false);
			rHead3.setEnabled(false);
			cbTm.setEnabled(true);
			cbDate.setEnabled(true);

			if (dfmt[DataFmt.HEAD_IDX].equals(DataFmt.HDR_AMES) ||
			    dfmt[DataFmt.HEAD_IDX].equals(DataFmt.HDR_ICARTT)) {
				NC2Act.wrtMsg(" Warning: High rate data netcdf file. ICARTT is nor supported.  ");
				dFormat.setDataFmt(DataFmt.HDR_PLAIN, DataFmt.HEAD_IDX);
			}
		}

		//head
		if (dfmt[DataFmt.HEAD_IDX].equals(DataFmt.HDR_AMES)) {
			rHead2.setSelected(true);
			cbTm.setSelectedIndex(3);	// Ames uses seconds since midnight
			cbDate.setSelectedIndex(2);	//noDate
			cbTm.setEnabled(false);
			cbDate.setEnabled(false);
		}
		if (dfmt[DataFmt.HEAD_IDX].equals(DataFmt.HDR_ICARTT)) {
			rHead3.setSelected(true);
			cbTm.setSelectedIndex(3);	// ICARTT uses seconds since midnight
			cbDate.setSelectedIndex(2);	//noDate
			cbTm.setEnabled(false);
			cbDate.setEnabled(false);
		}
		if (dfmt[DataFmt.HEAD_IDX].equals(DataFmt.HDR_NCML)) {
			rHead4.setSelected(true);
		}

		String item = dfmt[DataFmt.DATE_IDX];
		if (item.equals(DataFmt.DATESPACE)) {
			cbDate.setSelectedIndex(1);
		}
		if (item.equals(DataFmt.NODATE)) {
			cbDate.setSelectedIndex(2);
		}

		item = dfmt[DataFmt.TM_IDX];
		if (item.equals(DataFmt.TIMESPACE)) {
			cbTm.setSelectedIndex(1);
		}
		if (item.equals(DataFmt.TIMENOSPACE)) {
			cbTm.setSelectedIndex(2);
		}
		if (item.equals(DataFmt.TIMESEC)) {
			cbTm.setSelectedIndex(3);
		}

		if (dfmt[DataFmt.DMTR_IDX].equals(DataFmt.SPACEVAL)) {
			rDmtr.setSelected(false);
			rDmtr2.setSelected(true);
			rVal2.setEnabled(false);
			rVal2.setSelected(false);
			if (dfmt[DataFmt.MVAL_IDX]==null ||dfmt[DataFmt.MVAL_IDX].isEmpty() ){
				rVal.setEnabled(true);
				rVal.setSelected(true);
				dFormat.setDataFmt(DataFmt.MISSVAL, DataFmt.MVAL_IDX);
			}
		}

		if (dfmt[DataFmt.MVAL_IDX]==null || dfmt[DataFmt.MVAL_IDX].isEmpty()) {
			rVal2.setSelected(true);
			rVal.setSelected(false);
			rVal3.setSelected(false);
		} else 	if (dfmt[DataFmt.MVAL_IDX].equals(DataFmt.REPLICATE)) {
			rVal3.setSelected(true);
			rVal.setSelected(false);
			rVal2.setSelected(false);
		}

		if (!dfmt[DataFmt.TMSET_IDX].equals(DataFmt.FULLTM)) {
			rTmSet2.setSelected(true);
			rTmSet.setSelected(false);
			tfDateSet.setEnabled(true);
			tfTmSet.setEnabled(true);
			tfDateSet2.setEnabled(true);
			tfTmSet2.setEnabled(true);
			//parse tmset
			String[] tmset = dFormat.getTmSet().split(DataFmt.TMSETDELIMIT);
			tfDateSet.setText(tmset[0].split(DataFmt.COMMAVAL)[0]);
			tfTmSet.setText(tmset[0].split(DataFmt.COMMAVAL)[1]);
			tfDateSet2.setText(tmset[1].split(DataFmt.COMMAVAL)[0]);
			tfTmSet2.setText(tmset[1].split(DataFmt.COMMAVAL)[1]);
		}

		tfDisp.setText(refreshPreview());
	}
}
