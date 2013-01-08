//jslinky - No copyright, do what you will with me!

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
    
    //reused constant for imposing init conditions
    var tornado = k/(m*g);
    this._y[0] = this.y0;
    

    for(var i = 1; i < N; i++){
        dy = (N - i)/tornado;
        var nt = 0.0;
        if (dy > l1){
            nt = this._y[i-1] + dy;
            this.collapsed.push(false);
        }else{
            nt = false;
            this.collapsed.push(true);

            if ((i-1) < this.bottomcolT){
                this.bottomcolT = (i-1);

                }
        }
        this._y[i] = nt;
    }
}

//Slinky Functions ***************************
Slinky.prototype.y = function(){
        var rtnArray = new Array(this.N)
        for(var i = 0; i < this.N; i++){
            if(i < this.topcolT){
                rtnArray[i] = this._y[this.topcolT] - (this.topcolT - i)*this.l1;
            } else if ( (i >= this.topcolT) && (i <= this.bottomcolT) ){
                rtnArray[i] = this._y[i];
            } else {
                rtnArray[i] = this._y[this.bottomcolT] + (i - this.bottomcolT)*this.l1;
            }
        }
        return rtnArray;
    };
Slinky.prototype.draw = function(canvas){
    var ctx = canvas.getContext('2d');
    var cwidth = canvas.width;
    var cheight = canvas.height;
    var center = Math.ceil(cwidth/2);
    var ringHWidth = Math.ceil(cwidth/20);
    var l = center - ringHWidth;
    var r = center + ringHWidth;
    
    ctx.strokeStyle = 'red';
    ctx.beginPath();
    alert(this.topcolT);
    alert(this.bottomcolT);
    this.y().forEach(function(el,ind,ar){
        ctx.moveTo(l, el);
        ctx.lineTo(r, el);
        if(this.topcolT == ind){
            ctx.stroke();
            alert('done1');
            ctx.strokeStyle = 'blue';
            ctx.beginPath();
        }else if(this.bottomcolT == ind){
            ctx.stroke();
            alert('done2');
            ctx.strokeStyle = 'green';
            ctx.beginPath();
        }
    });
    ctx.stroke();
    
};


function draw(){
    var canvasID = 'tutorial'

    var canvas = document.getElementById(canvasID);
    canvas.height = 500;
    slin = new Slinky(20,1.0,2.0,1.0,1.0,1.0);
    slin.draw(canvas);
    
    alert('_y:' + slin._y.toString());
    alert('y:' + slin.y());
}
