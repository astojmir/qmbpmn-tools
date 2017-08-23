function DomSelect(objQry) {
    var qryNode = $(objQry.nodeId);
    if (!objQry.attrValue) {
	return [qryNode];
    }
    var qryObjs = $C(objQry.attrValue, objQry.attrName, qryNode, objQry.tag);
    return qryObjs;
}

function appendOptionLast(elSel, optText, optVal)
{
  var elOptNew = document.createElement('option');
  elOptNew.text = optText;
  elOptNew.value = optVal;
  try {
    elSel.add(elOptNew, null); // standards compliant; doesn't work in IE
  }
  catch(ex) {
    elSel.add(elOptNew); // IE only
  }
}

function setProperty(objQry, prop, val, stl) {

    var qryObjs = DomSelect(objQry);
    for (k=0; k<qryObjs.length;k++) {
	var o = qryObjs[k];
	if (stl) {
	    o.style[prop] = val;
	}
	else {
	    o[prop]= val;
	}
    }
}

function setMaster(objQry) {
    var qryObjs = DomSelect(objQry);
    for (k=0; k<qryObjs.length;k++) {
	var o = qryObjs[k];
	o.selected = true;
	selId = o.parentNode.id;
	changedMasterSelection(selId, o.index);
    }
}

function setSelection(objQry) {
    var qryObjs = DomSelect(objQry);
    for (k=0; k<qryObjs.length;k++) {
	var o = qryObjs[k];
	o.selected = true;
    }
}

function setMasterSelections(mSlct) {
    for (selId in mSlct) {
	var node = $(selId);
	var mSel = mSlct[selId];
	utils.removeChildren(node);
	for (k=0; k<mSel.mOpt.length;k++) {
	    appendOptionLast(node, mSel.mOpt[k].text, mSel.mOpt[k].value);
	}
	node.selectedIndex = 0;
	changedMasterSelection(selId, 0);
    }
}


function changedMasterSelection(selId, i)
{
    var mOpt = clientState.masterSelections[selId].mOpt[i];
    for (j=0; j<mOpt.sSel.length;j++) {
	var sSelId = mOpt.sSel[j].id;
	var sOpt = mOpt.sSel[j].sOpt;
	var node = $(sSelId);
	var old_val = node.value;
	utils.removeChildren(node);
	for (k=0; k<sOpt.length;k++) {
	    appendOptionLast(node, sOpt[k].text, sOpt[k].value);
	}
	var objQry = {"attrValue": old_val,
		      "attrName": "value",
		      "nodeId": sSelId,
		      "tag": "option"};
	setSelection(objQry);
    }
    for (j=0; j<mOpt.sProp.length;j++) {
	p = mOpt.sProp[j];
	setProperty(p.selector, p.property, p.value, p.style);
    }
}


function setupPage()
{
    setMasterSelections(clientState.masterSelections);
//     $("netgroup").selectedIndex = 0;
//     groupChange(0);
}

function groupChange(i)
{
    grp = $("netgroup").options[i].value;
    gs = $("graph");
    first = 1;
    for (j=0; j<gs.length;j++) {
	if (gs.options[j].getAttribute('group') == grp) {
	  gs.options[j].style["display"] = "block";
	  if (first) {
	      gs.options[j].selected = true;
	      first = 0;
	  }
	}
	else {
	  gs.options[j].style["display"] = "none";
	}
    }
    graphChange(gs.selectedIndex);
}

function graphChange(i)
{
    document.getElementById("antisink_map").value = graph_list[i].antisinks;
}

function resetParams()
{
    document.query_form.reset();
//     $("netgroup").selectedIndex = 0;
//     groupChange(0);
    $("graph").selectedIndex = 0;
    graphChange(0);
    resetDisplay();
}

function resetDisplay()
{
    document.display_form.reset();
    updateDisplayOptions();
}


function updateDisplayOptions() {

    var j = 0;
    // Set object values
    var props = clientState.formSettings.setProp;
    for (j=0; j<props.length;j++) {
	var qstr = props[j].selector;
	var prop = props[j].property;
	var val = props[j].value;
	var stl = parseInt(props[j].style);
	setProperty(qstr, prop, val, stl);
    }

    // Update master selections
    setMasterSelections(clientState.masterSelections);

    // Set master selections
    var props = clientState.formSettings.setMaster;
    for (j=0; j<props.length;j++) {
	setMaster(props[j]);
    }

    // Set other selections
    var props = clientState.formSettings.setSelect;
    for (j=0; j<props.length;j++) {
	setSelection(props[j]);
    }
}

function fillExample() {
    $("graph").selectedIndex = example_data.graph;
    graphChange(example_data.graph);
    for (k=0; k<example_data.boundary.length;k++) {
        node = $(example_data.boundary[k][0]);
        node.value = example_data.boundary[k][1];
    }
}
