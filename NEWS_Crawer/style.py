QSS = """
    QLabel{
    font-family: Helvetica;
    font-weight: normal;
    font-size: 9pt;
    color: tomato;
    }

    QComboBox {
    background-color: rgb(255,255,255);
    border: 1px solid lightgreen;
    selection-background-color: rgb(138,247,155);
    selection-color: rgb(200, 200, 200);
    font-family: Helvetica;
    font-weight: normal;
    font-size: 9pt;
    color: tomato;
    }
    QListView::item:selected {
    border: 1px solid #6a6ea9;
    }
    QListView {
	border-top: 4;
	border-left: 4;
	border-bottom: 4;
	border-right: 4;
	background-color: #C87020;
	font-family: Helvetica;
	color: #212121;
    }

    QListView::item, QListView::item:hover {
	border-image: url(:/Resources/Images/Panel2_Normal.png);
	border-top: 4;
	border-left: 4;
	border-bottom: 4;
	border-right: 4;
	background-color: LightCyan;
	font-family: Helvetica;
	color: tomato;
    }

    QListView::item:selected,  QListView::item:selected:active, QListView::item:selected:!active {
	border-top: 4;
	border-left: 4;
	border-bottom: 4;
	border-right: 4;
	background-color: LightSkyBlue;
	font-family: Helvetica;
	color: #212121;
    }
    QComboBox::downarrow {
    width: 1px;
    height: 1px; 
    }

    QLineEdit {
    background-color: rgb(255,255,255);
    border-top: none;
    border-left: none;
    border-right: none;
    border-bottom:1px solid lightgreen;
    font-family: Helvetica;
    font-weight: normal;
    font-size: 9pt;
    color: tomato;
    }
"""