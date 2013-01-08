//jslinky - No copyright, do what you will with me!


function canvas_arrow(context, fromx, fromy, tox, toy,headlen){
    var angle = Math.atan2(toy-fromy,tox-fromx);
    context.moveTo(fromx, fromy);
    context.lineTo(tox, toy);
    context.lineTo(tox-headlen*Math.cos(angle-Math.PI/6),toy-headlen*Math.sin(angle-Math.PI/6));
    context.moveTo(tox, toy);
    context.lineTo(tox-headlen*Math.cos(angle+Math.PI/6),toy-headlen*Math.sin(angle+Math.PI/6));
}

//Slinky object/consturctor
function Slinky(N, l0, l1, k, g, m) {
    //model params
    this.N = N;
    this.l0 = l0;
    this.l1 = l1;
    this.k = k;
    this.g = g;
    this.m = m;
        
    //implementation params
    this._y = new Array(N);
    this.collapsed = new Array(N-1);
    this.topcolT = 0;
    this.bottomcolT = N;
    this.axisRange = new Array(2);
    this.comy0 = 0;    
    this.y0 = 50.0;
    
    this._y[0] = this.y0;
    
    for(var i = 1; i < N; i++){
        dy = (N - i)*(m*g)/k;
        var nt = 0.0;
        if (dy > l1){
            nt = this._y[i-1] + dy;
            this.collapsed[i-1] = false;
        }else{
            nt = false;
            this.collapsed[i-1] = true;

            if ((i-1) < this.bottomcolT){
                this.bottomcolT = (i-1);

                }
        }
        this._y[i] = nt;
    }
    this.ylast = new Array();
}

//Slinky Functions ***************************
Slinky.prototype.y = function(turn){
    if(turn < this.topcolT){
        return (this._y[this.topcolT] - (this.topcolT - turn)*this.l1);
    } else if ( (turn >= this.topcolT) && (turn <= this.bottomcolT) ){
        return (this._y[turn]);
    } else {
        return (this._y[this.bottomcolT] + (turn - this.bottomcolT)*this.l1);
    }
}
Slinky.prototype.getYArray = function(){
    var rtnArray = new Array(this.N)
    for(var i = 0; i < this.N; i++){
        rtnArray[i] = this.y(i);
    }
    return rtnArray;
};
Slinky.prototype.ten = function(turn, ud){
    ten = 0.0
    //ten from above
    if( (ud & 1) && (turn != 0 ) && (this.collapsed[turn-1] == false) ){
        ten += this.k*(this.y(turn-1) - this.y(turn));
    }
    if( (ud & 2) && (turn != (this.N - 1)) && (this.collapsed[turn] == false) ){
        ten += this.k*(this.y(turn+1) - this.y(turn));
    }
    return ten;
};
Slinky.prototype.accel = function(turn){
    f = this.ten(turn,3);
    /*if( (this.collapsed[turn-1] == false) &&
        ( ( turn == this.collapsed.length )
        || ( this.collapsed[turn] == false) ) ){*/
    if((turn > this.topcolT) && ( turn < this.bottomcolT)){
           f -= this.m*this.g;
           return (f/this.m);
        }
    else if (turn == this.topcolT){
        f -= this.m*this.g*(this.topcolT + 1);
        return (f/(this.m*(this.topcolT + 1)));
    } else if(turn == this.bottomcolT){
        f -= this.m*this.g*(this.N - this.bottomcolT);
        return (f/(this.m*(this.N - this.bottomcolT)));
    }
};
Slinky.prototype.com = function(){
    sum = 0.0;
    for( var i=0; i < this.N; i++){
        sum += this.m*this.y(i);
    }
    return (sum/(this.m*this.N));
};
Slinky.prototype.advance = function(dt){
    if(this.ylast.length != this.N){
        this.ylast = this.getYArray().slice();
    }
    var ynext = new Array(this.N);
    var old = this.getYArray();
    
    //integrate to prospective new positions
    for(var i=0; i < this.N; i++){
        ynext[i] = (2.0*this.y(i) - this.ylast[i] + dt*dt*this.accel(i));
    }
    
    //enforce mmt conservation
    for(var i=0; i < this.N; i++){
        if( (i >= this.topcolT) && (i < this.bottomcolT)){
        
        }
    }
}
Slinky.prototype.draw = function(canvas){
    var ctx = canvas.getContext('2d');
    var cwidth = canvas.width;
    var cheight = canvas.height;
    var center = Math.ceil(cwidth/2);
    var ringHWidth = Math.ceil(cwidth/20);
    var l = center - ringHWidth;
    var r = center + ringHWidth;
    
    var ypos = this.getYArray();
    //draw slinky
    ctx.strokeStyle = 'red';
    ctx.beginPath();
    ypos.forEach(function(el,ind,ar){
        ctx.moveTo(l, el);
        ctx.lineTo(r, el);
        if(this.topcolT == ind){
            ctx.stroke();
            ctx.strokeStyle = 'blue';
            ctx.beginPath();
        }else if(this.bottomcolT == ind){
            ctx.stroke();
            ctx.strokeStyle = 'green';
            ctx.beginPath();
        }
    },this);
    ctx.stroke();
    
    //draw force arrows
    ctx.strokeStyle = 'brown';
    ctx.beginPath();
    ypos.forEach(function(el,ind,ar){
        if(this.ten(ind,3)){
            canvas_arrow(ctx,center,el,center,el+this.ten(ind,3),5);
        }
    },this);
    ctx.stroke();
    
    //draw com
    var com = this.com();
    ctx.strokeStyle = 'black';
    ctx.beginPath();
    ctx.moveTo(center-2,com);
    ctx.lineTo(center+2,com);
    ctx.moveTo(center,com+2);
    ctx.lineTo(center,com-2);
    ctx.stroke();
    ctx.fillText('CoM',r*1.1, com)
    
    sum = 0.0;
    ypos.forEach(function(el,ind,ar){
        sum += this.accel(ind);
    },this);
    
    //ctx.fillText(sum.toString(),r*1.3, com);

};


function draw(){
    var canvasID = 'tutorial'

    var canvas = document.getElementById(canvasID);
    canvas.height = 500;
    slin = new Slinky(20,1.0,2.0,1.0,1.0,1.0);
    slin.draw(canvas);
    
    //alert('_y:' + slin._y.toString());
    //alert('y:' + slin.y());
}
