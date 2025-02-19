from .tikzeng import *


def block_2ConvPool(name, botton, top, s_filer=256, n_filer=64, offset="(1,0,0)",
                    size=(32,32,3.5), opacity=0.5):
    return [
    to_ConvConvRelu( 
        name="ccr_{}".format( name ),
        s_filer=str(s_filer), 
        n_filer=(n_filer,n_filer), 
        offset=offset, 
        to="({}-east)".format( botton ), 
        width=(size[2],size[2]), 
        height=size[0], 
        depth=size[1],   
        ),    
    to_Pool(         
        name="{}".format( top ), 
        offset="(0,0,0)", 
        to="(ccr_{}-east)".format( name ),  
        width=1,         
        height=size[0] - int(size[0]/4), 
        depth=size[1] - int(size[0]/4), 
        opacity=opacity, ),
    to_connection( 
        "{}".format( botton ), 
        "ccr_{}".format( name )
        )
    ]

def block_Unconv(name, botton, top, s_filer=256, n_filer=64, offset="(1,0,0)",
                 size=(32,32,3.5), opacity=0.5):
    return [
        to_UnPool(  name='unpool_{}'.format(name),    offset=offset,    to="({}-east)".format(botton),         width=1,              height=size[0],       depth=size[1], opacity=opacity ),
        to_ConvRes( name='ccr_res_{}'.format(name),   offset="(0,0,0)", to="(unpool_{}-east)".format(name),    s_filer=str(s_filer), n_filer=str(n_filer), width=size[2], height=size[0], depth=size[1], opacity=opacity ),       
        to_Conv(    name='ccr_{}'.format(name),       offset="(0,0,0)", to="(ccr_res_{}-east)".format(name),   s_filer=str(s_filer), n_filer=str(n_filer), width=size[2], height=size[0], depth=size[1] ),
        to_ConvRes( name='ccr_res_c_{}'.format(name), offset="(0,0,0)", to="(ccr_{}-east)".format(name),       s_filer=str(s_filer), n_filer=str(n_filer), width=size[2], height=size[0], depth=size[1], opacity=opacity ),       
        to_Conv(    name='{}'.format(top),            offset="(0,0,0)", to="(ccr_res_c_{}-east)".format(name), s_filer=str(s_filer), n_filer=str(n_filer), width=size[2], height=size[0], depth=size[1] ),
        to_connection( 
            "{}".format( botton ), 
            "unpool_{}".format( name ) 
            )
    ]

def block_Res(num, name, botton, top, s_filer=256, n_filer=64, offset="(0,0,0)",
              size=(32,32,3.5), opacity=0.5):
    lys = []
    layers = [ *[ '{}_{}'.format(name,i) for i in range(num-1) ], top]
    for name in layers:        
        ly = [ to_Conv( 
            name='{}'.format(name),       
            offset=offset, 
            to="({}-east)".format( botton ),   
            s_filer=str(s_filer), 
            n_filer=str(n_filer), 
            width=size[2],
            height=size[0],
            depth=size[1]
            ),
            to_connection( 
                "{}".format( botton  ), 
                "{}".format( name ) 
                )
            ]
        botton = name
        lys+=ly
    
    lys += [
        to_skip( of=layers[1], to=layers[-2], pos=1.25),
    ]
    return lys
    
def layer_connection(layer, name, source, opacity=0.5, **kwargs):
    block = [
        layer(f"{name}_hide", to=f"({source}-east)", opacity=0, **kwargs),
        to_connection(source, f"{name}_hide"),
        layer(name, to=f"({source}-east)", opacity=opacity, **kwargs)
    ]
    return block

def a_Conv(name, source, height, depth, width, offset, width_label = "",
           depth_label = "", conv_first = True):
    # Wraps to_Conv with to_connection and to_Pool using layer_connection
    if conv_first:
        block = [
            *layer_connection(to_Conv, name, source, offset=offset,
                              s_filer=depth_label, n_filer=width_label,
                              height=height, depth=depth, width=width),
            to_Pool(name=f"{name}_activ", offset="(0,0,0)", to=f"({name}-east)",
                    height=height, depth=depth, width=1)
        ]
    else:
        block = [
            *layer_connection(to_Pool, f"pre_{name}_activ", source, offset=offset,
                              height=height, depth=depth, width=1),
            to_Conv(name, offset="(0,0,0)", to=f"(pre_{name}_activ-east)",
                    s_filer=depth_label, n_filer=width_label,
                    height=height, depth=depth, width=width)
        ]
    return block