(function() {
 var arronl = new Array();
  window.ao = {};

//_ returns (arguments || id if string) as array
  function _() {
   var e;
   var arr = new Array();
    for( var i=0; i<arguments.length; i++ ) {
      e = arguments[i];
      arr.push( typeof e == 'string' ? e != "" ? document.getElementById( e ) : null : e );
    }
    return arguments.length == 1 ? arr[0] : arr;
  }
  window.ao._ = _;
  function _t( e ) {
    if( typeof e == 'undefined' ) e = window.event;  
    if( typeof e.target != 'undefined' ) return e.target;
    if (typeof e.srcElement != 'undefined') return e.srcElement;  
    return null;
  }
// addEvent
  window.ao.addEvent = function( e, evType, fn ) {
    if( !(e = _( e )) ) return false;
    if( e.addEventListener ) { e.addEventListener( evType, fn, false ); return true; }
    if( e.attachEvent      ) return e.attachEvent( "on" + evType, function() { return fn( window.event ); } );
    /* else */                 e['on' + evType] = fn;
    return true;
  };
// setEvent
  window.ao.setEvent = function( e, eType, fn ) { 
    if( !!(e = _( e )) ) {
      var f = function( e ) { 
        if( (e || window.event) == null ) return false;
        e.cancelBubble = true;
        if( e.stopPropagation ) e.stopPropagation();
        if (e.preventDefault) e.preventDefault();
        else if( window.event ) window.event.returnValue = false;
        fn( e );
        return true;
      };
      if( typeof fn != 'function' ) e['on' + eType] = undefined;
      else if( e.addEventListener ) e.addEventListener( eType, f, false ); //bubbling
      else if( e.attachEvent ) e.attachEvent( "on" + eType, f );
      else e['on' + eType] = f;
    }
  };
// addOnLoad event
  window.ao.addOnLoad = function( func ) {
    arronl.push( func );
  };
//toggle
  window.ao.toggle = function( e ) { 
    var r, s;
    if( (e || window.event) == null ) return false;
    e = e.srcElement ? e.srcElement : e.target;
    while ( e && e.nodeType != 1 ) e = e.parentNode;
    if( e ) {
      r = RegExp( "showing" );
      e.className = e.className.match( r ) 
                  ? e.className.replace( r, "hiding" ) 
                  : e.className.replace( RegExp( "hiding" ), "showing" );
      e = e.id;
      if( e ) {
        s = RegExp( "shown" );
        e = e.replace( RegExp( "(Help|Toggle)$" ), "" );
        if( e ) e = _( e );
        if( e ) e.className = e.className.match( s ) 
                            ? e.className.replace( s, "hidden" )
                            : e.className.replace( RegExp( "hidden" ), "shown" );
      }
      return true;
    }
    return false;
  };
//toggle to shown
  window.ao.toggleon = function( e ) { 
    var r, s;
    if( !!(e = _( e )) ) {
      if( !e.className.match( RegExp( "showing" ) ) ) {
        e.className = e.className.replace( RegExp( "hiding" ), "showing" );
      }
      e = e.id;
      if( e ) {
        s = RegExp( "shown" );
        e = e.replace( RegExp( "(Help|Toggle)$" ), "" );
        if( e ) e = _( e );
        if( e && !e.className.match( s ) ) {
          e.className = e.className.replace( RegExp( "hidden" ), "shown" );
        }
      }
      return true;
    }
    return false;
  };
//toggle to hide
  window.ao.toggleoff = function( e ) { 
    var r, s;
    if( !!(e = _( e )) ) {
      if( !e.className.match( RegExp( "hiding" ) ) ) {
        e.className = e.className.replace( RegExp( "showing" ), "hiding" );
      }
      e = e.id;
      if( e ) {
        s = RegExp( "hidden" );
        e = e.replace( RegExp( "(Help|Toggle)$" ), "" );
        if( e ) e = _( e );
        if( e && !e.className.match( s ) ) {
          e.className = e.className.replace( RegExp( "shown" ), "hidden" );
        }
      }
      return true;
    }
    return false;
  };
//toggle
  window.ao.toggleselect = function( e ) { 
    if( (e || window.event) == null ) return false;
    e = e.srcElement ? e.srcElement : e.target;
    while ( e && e.nodeType != 1 ) e = e.parentNode;
    return ao.updateselect( e );
  };
//update select options
  window.ao.updateselect = function( e ) {  
   var i, s, o;
    if( !!(s = e) ) {
      if( !!(e = e.id) ) {
        e = e.replace( /Toggle/, "" );
        for( i=0; i<s.options.length; i++ ) {
          if( !!(o = _( e + i )) ) o.className = o.className.replace( /shown|hidden/, s.options[i].selected ? "shown" : "hidden" );
        }
      }
      return true;
    }
    return false;
  };
// Cookies
  window.ao.delCookie = function( name ) {
    var e,a;
    var d = new Date();
    d.setTime( d.getTime() - 24 * 60 * 60 * 1000 );
    for( e="domain=.nlm.nih.gov;"; e!="domain=;"; e=e.replace(/=\.*\w+/,"=") )
      document.cookie = name + "=; expires=" + d.toGMTString() + "; " + e + " path=/";
  };
  window.ao.setCookie = function( name, value, days ) {
   var e = "";
    ao.delCookie( name );
    if( !!days ) {
     var d = new Date();
      d.setTime( d.getTime() + days*24*60*60*1000 );
      e = "; expires=" + d.toGMTString();
    }
    document.cookie = name + "=" + value + e + "; domain=.nlm.nih.gov; path=/";
  };
  window.ao.getCookie = function( name ) {
   var s = name + "=";
   var arr = document.cookie.split( ';' );
    for( var i=0; i<arr.length; i++ ) {
      for( var c=arr[i]; c.charAt(0)==' '; ) c = c.substring( 1, c.length );
      if( c.indexOf( s ) == 0 ) return c.substring( s.length, c.length );
    }
    return "";
  };
//Input cookies
  window.ao.getinput = function( e, c ) {
   var a, i;
    c = ao.getCookie( c );
    if( !!(e = _( e )) ) {
      a = e.getElementsByTagName( 'input' );
      for( i=0; i<a.length; i++ ) if( a[i].name != "" ) {
        c = c.replace( RegExp( "(^|#)" + a[i].name + "#[^#]+", "g" ), "" );
        if( a[i].type == 'text' ) { 
          if( a[i].value != a[i].defaultValue     ) c += "#" + a[i].name + "#" +  a[i].value;
        } else if( a[i].type == 'checkbox' ) {
          if( a[i].checked != a[i].defaultChecked ) c += "#" + a[i].name + "#x" + (a[i].checked ? "1" : "0");
        }
      }
    }
    return c.replace( /^#/, "" );
  };
  window.ao.definput = function( e, c ) {
   var a, i;
    c = ao.getCookie( c );
    if( !!(e = _( e )) ) {
      a = e.getElementsByTagName( 'input' );
      for( i=0; i<a.length; i++ ) if( a[i].name != "" ) 
        c = c.replace( RegExp( "(^|#)" + a[i].name + "#[^#]+", "g" ), "" );
    }
    return c.replace( /^#/, "" );
  };
  window.ao.getselect = function( e, c ) {
   var a, i, k;
    c = ao.getCookie( c );
    if( !!(e = _( e )) ) {
      a = e.getElementsByTagName( 'select' );
      for( i=0; i<a.length; i++ ) {
        c = c.replace( RegExp( "(^|#)" + a[i].name + "#[^#]+", "g" ), "" );
        for( k=0; k<a[i].options.length; k++ ) {
          if( a[i].options[k].selected != a[i].options[k].defaultSelected ) c += "#" + a[i].name + "#" + k;
        }
      }
    }
    return c.replace( /^#/, "" );
  };
  window.ao.defselect = function( e, c ) {
   var a, i, k;
    c = ao.getCookie( c );
    if( !!(e = _( e )) ) {
      a = e.getElementsByTagName( 'select' );
      for( i=0; i<a.length; i++ ) 
        c = c.replace( RegExp( "(^|#)" + a[i].name + "#[^#]+", "g" ), "" );
    }
    return c.replace( /^#/, "" );
  };
  window.ao.setinput = function( e, s ) {
   var a, i, k;
    if( !!(e = _( e )) && !!s ) {
      if( !!(a = s.split( "#" )) ) for( i=1; i<a.length; i+=2 ) {
        s = document.getElementsByName( a[i - 1] );
        if( s ) for( k=0; k<s.length; k++ ) if( !!(e = s[k]) ) {
          if(      a[i] == "x1" ) e.checked = true;
          else if( a[i] == "x0" ) e.checked = false;
          else                    try { e.value = a[i]; } catch( e ) { ; };
        }
      }
    }
  };
  window.ao.setselect = function( e, s ) {
   var a, i, k;
    if( !!(e = _( e )) && !!s ) {
      a = s.split( "#" );
      for( i=1; i<a.length; i+=2 ) {
        s = document.getElementsByName( a[i - 1] );
        for( k=0; k<s.length; k++ ) if( !!(e = s[k]) && e.options[a[i]] ) e.options[a[i]].selected = !e.options[a[i]].defaultSelected; 
      }
    }
  };
//Dialogs
var mousex = 0;
var mousey = 0;
var grabx = 0;
var graby = 0;
var orix = 0;
var oriy = 0;
var oriw = 0;
var orih = 0;
var odrag= 0;

var dragobj = null;
var onmupd;
var onname;
 
  function mouseupdate( e ) {
    e = e || window.event;
    mousex = e.pageX || (e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft);
    mousey = e.pageY || (e.clientY + document.body.scrollTop  + document.documentElement.scrollTop );
  } 
  function drag( e ) {
   var r = document.body.getBoundingClientRect();
   var z = (r.right - r.left)/document.body.offsetWidth;
    mouseupdate( e );
    if( dragobj ) {
/*      dragobj.style.position = "absolute"; */
      if( odrag& 1 ) dragobj.style.top    = Math.round( oriy + (mousey - graby)/z ).toString(10) + 'px';
      if( odrag& 2 ) dragobj.style.left   = Math.round( orix + (mousex - grabx)/z ).toString(10) + 'px';
      if( odrag& 4 ) dragobj.style.width  = Math.round( oriw + (grabx - mousex)/z ).toString(10) + 'px';
      if( odrag& 8 ) dragobj.style.height = Math.round( orih + (graby - mousey)/z ).toString(10) + 'px';
      if( odrag&16 ) dragobj.style.width  = Math.round( oriw + (mousex - grabx)/z ).toString(10) + 'px';
      if( odrag&32 ) dragobj.style.height = Math.round( orih + (mousey - graby)/z ).toString(10) + 'px';
      if( navigator.appName.indexOf("Microsoft") != -1 ) {
        var z = document.getElementById( "d_aatest" );
        var y = document.createElement("div");
        var x = z.parentNode;
        y.id  = z.id;
        y.className   = z.className;
        y.innerHTML   = z.innerHTML;
        y.onmousedown = z.onmousedown;
        x.removeChild( z );
        x.appendChild( y );
      }
    }
    return false;
  }
  function drop( e ) {
    dragobj = null;
    mouseupdate( e );
    ao.setEvent( document, "mousemove", null );
    ao.setEvent( document, "mouseup",   null );
    ao.setEvent( document, "mousedown", null );
  } 
  window.ao.dialogs_init = function( name ) { onmupd = document.onmousemove; document.onmousemove = mouseupdate; onname = name; }
  window.ao.dialogs_term = function() { document.onmousemove = onmupd; }
  window.ao.grab = function( e ) { //Grab
    mouseupdate( e );
    e = e || window.event;
    if( e.preventDefault ) e.preventDefault();
    else window.event.returnValue = false;
    if( e == null ) return false;
    for( e=e.srcElement?e.srcElement:e.target; e&&e.nodeType!=1; ) e = e.parentNode;
    if( e ) {
      ao.setEvent( document, "mousemove", drag );
      ao.setEvent( document, "mouseup",   drop );
      ao.setEvent( document, "mousedown", function(){ return false; } );
      odrag = parseInt( e.className.match( /d_(\d+)/ )[1] );
      for( ; e.parentNode; e=e.parentNode ) if( e.id.match( /dlg/ ) ) break;
      dragobj = e;
      grabx = mousex;
      graby = mousey;
      for( orix=oriy=0; e; e=e.offsetParent ) {
        orix += e.offsetLeft;
        oriy += e.offsetTop;
      }
      var z;
      z = document.body.getBoundingClientRect();
      z = (z.right - z.left)/document.body.offsetWidth;
      orix = Math.round( orix/z );
      oriy = Math.round( oriy/z );
      oriw = Math.round( dragobj.offsetWidth  );
      orih = Math.round( dragobj.offsetHeight );
      return true;
    }
    return false;
  };
//Print Obj
  window.ao.printObj = function( oObj ) {
   var s = "";
    for( var i in oObj ) s += " " + i + " : [" + (typeof oObj[i]) + "] : " + oObj[i] + "\n";
    return s;
  }
  window.ao.initgtgl = function() {
  var a, i, f;
    a = document.getElementsByTagName( 'a' );
    if( a ) for( i=0; i<a.length; i++ ) {
      if( a[i].id.match( /^gtgl/ ) ) 
        ao.addEvent( a[i], 'click', function ( e ) { //a
         var ea, id, dv;
          if( (e = e || window.event) == null ) return false;
          if( e.preventDefault ) e.preventDefault();
          else if( window.event ) window.event.returnValue = false;
          e = e.srcElement ? e.srcElement : e.target;
          while( e && e.nodeType != 1 ) e = e.parentNode;
          if( !e.id.match( /^gtgl(.*)$/ ) ) return false;
          id = RegExp.$1;
          id = id.replace( RegExp( "_$" ), "" );
          if( !!(ea = document.getElementsByTagName( 'div' )) ) for( i=0; i<ea.length; i++ ) {
            if( ea[i].id.match( /^gtgl(.*)(\w)$/ ) ) {
              dv = RegExp.$1;
              if( RegExp.$2 == "a" ) {
                if( id.match( RegExp( "^" + RegExp.$1 ) ) ) 
                  ea[i].className = dv == id && ea[i].className.match( RegExp( "expanded" ) )
                                  ? ea[i].className.replace( RegExp( "expanded" ), "collapsed" )
                                  : ea[i].className.replace( RegExp( "collapsed" ), "expanded" );
                else
                  ea[i].className = ea[i].className.replace( RegExp( "expanded" ), "collapsed" );
              } else if( RegExp.$2 == "b" ) {
                if( id.match( RegExp( "^" + RegExp.$1 ) ) ) 
                  ea[i].className = dv == id && ea[i].className.match( RegExp( "opened" ) )
                                  ? ea[i].className.replace( RegExp( "opened" ), "closed" )
                                  : ea[i].className.replace( RegExp( "closed" ), "opened" );
                else                                        
                  ea[i].className = ea[i].className.replace( RegExp( "opened" ), "closed" );
              }
            }
          }
          return true;
      });
    }
  };
  function _cat() {
   var a, i;
    a = document.getElementsByTagName( "span" );
    for( i=0; i<a.length; i++ ) if( a[i].className == "cat" ) a[i].innerHTML = "@";
    a = document.getElementsByTagName( "a" );
    for( i=0; i<a.length; i++ ) if( a[i].className == "cat" ) a[i].href = "mailto:" + a[i].innerHTML.replace( /<(|\/)span[^>]*>/gi, "" );
  }
  window.ao.load = function() { 
    for( var i=0; i<arronl.length; i++ ) 
      arronl[i]();
  };
  ao.addOnLoad( _cat );
  ao.addOnLoad( ao.initgtgl );
})();
// window.onload = ao.load;
